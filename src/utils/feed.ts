import type { APIContext, ImageMetadata } from 'astro'
import type { CollectionEntry } from 'astro:content'
import type { Author } from 'feed'
import { getImage } from 'astro:assets'
import { getCollection } from 'astro:content'
import { Feed } from 'feed'
import MarkdownIt from 'markdown-it'
import { parse as htmlParser } from 'node-html-parser'
import sanitizeHtml from 'sanitize-html'
import { defaultLocale, themeConfig } from '@/config'
import { ui } from '@/i18n/ui'
import { memoize } from '@/utils/cache'
import { generateDescription } from '@/utils/description'

interface GenerateFeedOptions {
  lang?: string
}

const markdownParser = new MarkdownIt()
const { title, description, url, author: siteAuthor } = themeConfig.site
const followConfig = themeConfig.seo?.follow

// Dynamically import all images from /src/content/posts/_images
const imagesGlob = import.meta.glob<{ default: ImageMetadata }>(
  '/src/content/posts/_images/**/*.{jpeg,jpg,png,gif,webp}',
)

/**
 * Optimize image URLs
 *
 * @param srcPath Source relative path of the image
 * @param baseUrl Base URL of the site
 * @returns Optimized full image URL or null
 */
const getOptimizedImageUrl = memoize(async (srcPath: string, baseUrl: string) => {
  const prefixRemoved = srcPath.replace(/^\.\.\/|^\.\//, '')
  const rawImagePath = `/src/content/posts/${prefixRemoved}`
  const rawImageModule = imagesGlob[rawImagePath]

  if (!rawImageModule) {
    return null
  }

  const rawImageMetadata = await rawImageModule().then(res => res.default).catch(() => null)
  if (!rawImageMetadata) {
    return null
  }

  const processedImageData = await getImage({ src: rawImageMetadata })
  return new URL(processedImageData.src, baseUrl).toString()
})

/**
 * Fix relative image paths in HTML content
 *
 * @param htmlContent HTML content string
 * @param baseUrl Base URL of the site
 * @returns Processed HTML string with all image paths converted to absolute URLs
 */
async function fixRelativeImagePaths(htmlContent: string, baseUrl: string): Promise<string> {
  const htmlDoc = htmlParser(htmlContent)
  const images = htmlDoc.getElementsByTagName('img')
  const imagePromises = []

  for (const img of images) {
    const src = img.getAttribute('src')

    if (!src) {
      continue
    }

    imagePromises.push((async () => {
      try {
        // Skip if not a relative or public image path
        if (!src.startsWith('./') && !src.startsWith('../') && !src.startsWith('/images')) {
          return
        }

        // Process images from src/content/posts/_images directory
        if (src.startsWith('./') || src.startsWith('../')) {
          const optimizedImageUrl = await getOptimizedImageUrl(src, baseUrl)

          if (optimizedImageUrl) {
            img.setAttribute('src', optimizedImageUrl)
          }
          return
        }

        // Process images from public/images directory
        const publicImageUrl = new URL(src, baseUrl).toString()
        img.setAttribute('src', publicImageUrl)
      }
      catch (error) {
        console.warn(`Failed to process image in RSS feed: ${src}`, (error as Error)?.message ?? String(error))
      }
    })())
  }

  await Promise.all(imagePromises)
  return htmlDoc.toString()
}

/**
 * Generate post URL with language prefix and abbrlink/slug
 *
 * @param post The post collection entry
 * @param baseUrl Base URL of the site
 * @returns The fully formed URL for the post
 */
function generatePostUrl(post: CollectionEntry<'posts'>, baseUrl: string): string {
  const postSlug = post.data.abbrlink || post.id
  const langPrefix = post.data.lang !== defaultLocale && post.data.lang !== ''
    ? `${post.data.lang}/`
    : ''

  return new URL(`${langPrefix}posts/${postSlug}/`, baseUrl).toString()
}

/**
 * Generate a feed object supporting both RSS and Atom formats
 *
 * @param options Feed generation options
 * @param options.lang Optional language code
 * @returns A Feed instance ready for RSS or Atom output
 */
export async function generateFeed({ lang }: GenerateFeedOptions = {}) {
  const currentUI = ui[lang as keyof typeof ui] ?? ui[defaultLocale as keyof typeof ui] ?? {}
  const useI18nTitle = themeConfig.site.i18nTitle
  const siteTitle = useI18nTitle ? currentUI.title : title
  const siteDescription = useI18nTitle ? currentUI.description : description
  const baseUrl = lang ? `${url}/${lang}` : url
  const siteURL = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
  const author: Author = {
    name: siteAuthor,
    link: url,
  }

  // Create Feed instance
  const feed = new Feed({
    title: siteTitle,
    description: siteDescription,
    id: siteURL,
    link: siteURL,
    language: lang || themeConfig.global.locale,
    copyright: `Copyright © ${new Date().getFullYear()} ${siteAuthor}`,
    updated: new Date(),
    generator: 'Astro-Theme-Retypeset with Feed for Node.js',
    feedLinks: {
      rss: new URL(lang ? `/${lang}/rss.xml` : '/rss.xml', url).toString(),
      atom: new URL(lang ? `/${lang}/atom.xml` : '/atom.xml', url).toString(),
    },
    author,
  })

  // Filter posts by language and exclude drafts
  const posts = await getCollection(
    'posts',
    ({ data }: { data: CollectionEntry<'posts'>['data'] }) =>
      (!data.draft && (data.lang === lang || data.lang === '' || (lang === undefined && data.lang === defaultLocale))),
  )

  // Sort posts by published date in descending order and limit to the latest 25
  const limitedPosts = [...posts]
    .sort((a, b) => new Date(b.data.published).getTime() - new Date(a.data.published).getTime())
    .slice(0, 25)

  // Add posts to feed
  for (const post of limitedPosts) {
    const postLink = generatePostUrl(post, siteURL)

    // Optimize content processing
    const postContent = post.body
      ? sanitizeHtml(
          await fixRelativeImagePaths(
            // Remove HTML comments before rendering markdown
            markdownParser.render(post.body.replace(/<!--[\s\S]*?-->/g, '')),
            url,
          ),
          {
            // Allow <img> tags in feed content
            allowedTags: sanitizeHtml.defaults.allowedTags.concat(['img']),
          },
        )
      : ''

    // publishDate -> Atom:<published>, RSS:<pubDate>
    const publishDate = new Date(post.data.published)
    // updateDate -> Atom:<updated>, RSS has no update tag
    const updateDate = post.data.updated ? new Date(post.data.updated) : publishDate

    feed.addItem({
      title: post.data.title,
      id: postLink,
      link: postLink,
      description: generateDescription(post, 'feed'),
      content: postContent,
      author: [author],
      published: publishDate,
      date: updateDate,
    })
  }

  // Add follow verification if available
  if (followConfig?.feedID && followConfig?.userID) {
    feed.addExtension({
      name: 'follow_challenge',
      objects: {
        feedId: followConfig.feedID,
        userId: followConfig.userID,
      },
    })
  }

  return feed
}

/**
 * Generate RSS 2.0 format feed
 *
 * @param context Astro API context containing request params
 * @returns Response object with RSS XML content
 */
export async function generateRSS(context: APIContext) {
  const feed = await generateFeed({
    lang: context.params?.lang as string | undefined,
  })

  let rssXml = feed.rss2()
  rssXml = rssXml.replace(
    '<?xml version="1.0" encoding="utf-8"?>',
    '<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet href="/feeds/rss-style.xsl" type="text/xsl"?>',
  )

  return new Response(rssXml, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
    },
  })
}

/**
 * Generate Atom 1.0 format feed
 *
 * @param context Astro API context containing request params
 * @returns Response object with Atom XML content
 */
export async function generateAtom(context: APIContext) {
  const feed = await generateFeed({
    lang: context.params?.lang as string | undefined,
  })

  let atomXml = feed.atom1()
  atomXml = atomXml.replace(
    '<?xml version="1.0" encoding="utf-8"?>',
    '<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet href="/feeds/atom-style.xsl" type="text/xsl"?>',
  )

  return new Response(atomXml, {
    headers: {
      'Content-Type': 'application/atom+xml; charset=utf-8',
    },
  })
}

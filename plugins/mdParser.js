import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'
import rehypeParse from 'rehype-parse'
import rehypeMinifyWhitespace from 'rehype-minify-whitespace'

import jsonCompiler from '@nuxt/content/parsers/markdown/compilers/json.js'
import { defaultSchema } from '@/assets/sanitizeSchema.js'

// TODO: This pugin should be used to clean a lot of deplucated code.
// ALso, this plugin should have 2 mode one that send a JSON content and an other that send an HTML String
// Both should start from an MD or HTML String.
export default (_, inject) => {
  const mdCompiler = unified().use(remarkParse)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSanitize, defaultSchema)
    .use(rehypeStringify)
    .use(jsonCompiler)

  const mdParser = unified()
    .use(remarkParse)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSanitize, defaultSchema)
    .use(rehypeStringify)

  const markdownProcessor = unified()
    .use(remarkParse)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSanitize, defaultSchema)
    .use(rehypeMinifyWhitespace)
    .use(jsonCompiler)

  const htmlProcessor = unified()
    .use(rehypeParse)
    .use(rehypeSanitize, defaultSchema)
    .use(rehypeMinifyWhitespace)
    .use(jsonCompiler)

  inject('md', {
    parse (text) {
      return mdParser.processSync(text).contents
    },
    compile (text) {
      return mdCompiler.processSync(text).result
    },
    processMarkdown (text) {
      return markdownProcessor.processSync(text).result
    },
    processHtml (text) {
      return htmlProcessor.processSync(text).result
    }
  })
}

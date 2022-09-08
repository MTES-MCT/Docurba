import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'

import jsonCompiler from '@nuxt/content/parsers/markdown/compilers/json.js'
import { defaultSchema } from '@/assets/sanitizeSchema.js'

// TODO: This pugin should be used to clean a lot of deplucated code.
// ALso, this plugin should have 2 mode one that send a JSON content and an other that send an HTML String
// Both should start from an MD or HTML String.
export default (_, inject) => {
  const mdParser = unified().use(remarkParse)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSanitize, defaultSchema)
    .use(rehypeStringify)
    .use(jsonCompiler)

  inject('mdParse', (text) => {
    return mdParser.processSync(text).result
  })
}

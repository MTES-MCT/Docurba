import axios from 'axios'
import pdfMake from 'pdfmake/build/pdfmake'
import { A4 } from 'pdfmake/src/standardPageSizes'
import mixin from '@/mixins/orderSections.js'
import departements from '@/assets/data/INSEE/departements_small.json'

// import pdfFonts from 'pdfmake/build/vfs_fonts'
// pdfMake.vfs = pdfFonts.pdfMake.vfs

// This is only to speed up in test. Do not push in prod.
// import sections from '@/assets/test/sections.json'

const SOURCE_LABEL = {
  BASE_TERRITORIALE: 'Base territoriale',
  GEORISQUES: 'GéoRisques',
  INPN: 'INPN'
}

export default ({ $md, $isDev, $supabase }, inject) => {
  const baseUrl = $isDev ? 'http://localhost:3000' : location.origin

  // see https://github.com/MTES-MCT/Docurba/issues/61#issuecomment-1781502206
  const IMAGES_TO_REPLACE = {
    'https://sante.gouv.fr/local/adapt-img/608/10x/IMG/jpg/Etat_de_sante_population.jpg?1680693100': `${baseUrl}/images/Etat_de_sante_population.jpg`,
    'https://lh4.googleusercontent.com/iw_QbyDpmWeaIpHvqGXuugWtrHxRSRSAIijQ7qIZhg6QVFEvVkTcBXbnoGUobHmTHvwT43aRCxuuvarl-84pdJo7I0YkY7rYJgZFGqrN5lvql59O0J_KvLpO1jZIdqUzXCNjIeAdikbS4vKr8CBuTjg': `${baseUrl}/images/ORT.png`
  }

  const NARROW_NOBREAK_SPACE = ' '

  const PAGE_MARGINS = 40

  pdfMake.fonts = {
    Marianne: {
      normal: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Regular.otf`,
      bold: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Bold.otf`,
      italics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-RegularItalic.otf`,
      bolditalics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-BoldItalic.otf`
    }
  }

  const pdfMaker = {
    pdfFromContent (pdfData, filename = 'PAC') {
      Object.assign(pdfData, {
        pageSize: 'A4',
        pageMargins: PAGE_MARGINS,
        styles: {
          title: { fontSize: 40, alignment: 'center' },
          tocTitle: { fontSize: 18 },
          h1: { fontSize: 24, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          h2: { fontSize: 20, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          h3: { fontSize: 18, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          h4: { fontSize: 16, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          h5: { fontSize: 14, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          h6: { fontSize: 12, bold: true, alignment: 'left', margin: [0, 0, 0, 12] },
          mark: { background: '#ffff00' },
          a: { decoration: 'underline', color: '#000091' },
          p: { fontSize: 10, alignment: 'justify', margin: [0, 0, 0, 10] },
          img: { margin: [0, 0, 0, 10] },
          list: { margin: [0, 0, 0, 10] },
          table: { margin: [0, 0, 0, 10] },
          th: { fillColor: '#f1f3f5', bold: true },
          footer: { fontSize: 10, alignment: 'right' },
          ddt: { fontSize: 10, alignment: 'right' }
        },
        defaultStyle: {
          font: 'Marianne',
          fontSize: 10,
          lineHeight: 1.1,
          alignment: 'justify'
        },
        footer (currentPage, pageCount) {
          return {
            text: currentPage > 1 ? `${currentPage.toString()}` : '', // /${pageCount}`,
            style: 'footer',
            margin: [40, 10]
          }
        },
        pageBreakBefore (currentNode, followingNodesOnPage, nodesOnNextPage, previousNodesOnPage) {
          const isBreakedTitle = typeof (currentNode.style) === 'string' && currentNode.style?.includes('h') && currentNode.pageNumbers.length > 1
          return currentNode.headlineLevel === 1 || !!previousNodesOnPage.find(n => n.style === 'title') || isBreakedTitle
        }
      })

      pdfMake.createPdf(pdfData).download(`${filename}.pdf`)
    },
    // fetchGithubRef could go into its own plugin/mixin.
    async fetchGithubRef (githubRef, project) {
      const { data: sections } = await axios({
        method: 'get',
        url: `${baseUrl}/api/trames/tree/${githubRef}?content=all`
      })

      const { data: supSections } = await $supabase.from('pac_sections')
        .select('*')
        .in('ref', window.$nuxt.$options.filters.allHeadRefs(githubRef, project))

      mixin.methods.orderSections(sections, supSections)

      const { data: attachments } = await $supabase.from('pac_sections_data').select('*').eq('ref', githubRef)

      function pushAttachments (section) {
        const sectionAttachments = attachments.filter(a => a.path === section.path)
        if (sectionAttachments.length) {
          const attachmentElements = []

          for (const attachment of sectionAttachments) {
            attachmentElements.push(
              {
                type: 'element',
                tag: 'li',
                children: [
                  {
                    type: 'element',
                    tag: 'a',
                    props: {
                      href: attachment.url
                    },
                    children: [
                      {
                        type: 'text',
                        value: `${SOURCE_LABEL[attachment.source]} - ${attachment.category ? (attachment.category + ' - ') : ''}${attachment.title}`
                      }
                    ]
                  }
                ]
              }
            )
          }

          section.body.children.push({
            type: 'element',
            tag: 'ul',
            props: {},
            children: attachmentElements
          })
        }
      }

      function parseSection (section, paths) {
        if (section.content) {
          if (section.content.startsWith('<')) {
            section.body = $md.processHtml(section.content)
          } else {
            section.body = $md.processMarkdown(section.content)
          }
        }

        pushAttachments(section)

        if (section.children) {
          if (paths) {
            section.children = section.children.filter(c => paths.includes(c.path))
          }
          section.children.forEach(c => parseSection(c, paths))
        }
      }

      const selectedSections = project?.PAC
      const parsedSections = selectedSections ? sections.filter(s => selectedSections.includes(s.path)) : sections
      parsedSections.forEach(s => parseSection(s, selectedSections))

      return parsedSections
    },
    async pdfFromRef (githubRef, project) {
      const roots = await this.fetchGithubRef(githubRef, project)

      const dept = departements.find(d => d.code === project?.trame)

      const pdfContent = {
        content: [
          {
            columns: [
              {
                width: 100,
                fit: [100, 100],
                image: 'logo'
              }, {
                width: '*',
                text: project ? `Direction départementale des territoires \n ${dept.intitule}` : '',
                style: 'ddt'
              }
            ]
          },
          {
            text: this.getTitle(githubRef, project),
            style: 'title',
            margin: [0, 200, 0, 0]
          },
          {
            toc: { title: { text: 'SOMMAIRE' } }
          }
        ],
        images: {
          logo: `${baseUrl}/images/Republique_Francaise.jpg`
        }
      }

      function extractText (elements, params = {}) {
        return elements.map((element) => {
          const content = Object.assign({
            text: '\n',
            style: element.tag
          }, params)

          const newParams = {}

          if (element.tag === 'a' || params.tag === 'a') {
            content.link = element.props.href || params.link
            newParams.link = element.props.href || params.link
            newParams.style = 'a'
          }

          if (element.tag === 'strong' || element.bold) {
            newParams.bold = true
          }

          if (element.tag === 'em' || element.italics) {
            newParams.italics = true
          }

          if (element.tag === 'mark') {
            newParams.style = 'mark'
          }

          if (element.children && element.children.length) {
            content.text = extractText(element.children, Object.assign({}, params, newParams))
          } else if (!element.children) {
            content.text = element.value?.replaceAll(NARROW_NOBREAK_SPACE, ' ') || element
          }

          return content
        })
      }

      function transformElementToContent (element) {
        const headlineLevel = element.headlineLevel

        if (!element.tag) {
          return {
            text: element.value || element,
            headlineLevel
          }
        }

        if (/^h[1-6]$/.test(element.tag)) {
          const text = extractText(element.children)

          if (text.length) {
            return {
              text,
              style: element.tag,
              headlineLevel
            }
          }
        }

        if (element.tag === 'ul' || element.tag === 'ol') {
          return {
            [element.tag]: element.children.map(listItem => ({
              style: listItem.tag, // li
              stack: listItem.children.map(listItemChild => transformElementToContent(listItemChild))
            })),
            headlineLevel,
            style: 'list'
          }
        }

        if (element.tag === 'img' && element.props.src) {
          if (IMAGES_TO_REPLACE[element.props.src]) {
            // see https://github.com/MTES-MCT/Docurba/issues/61#issuecomment-1781502206
            element.props.src = IMAGES_TO_REPLACE[element.props.src]
          }

          if ($isDev && element.props.src.startsWith('https://docurba.beta.gouv.fr')) {
            element.props.src = element.props.src.replace('https://docurba.beta.gouv.fr', baseUrl)
          }

          const maxWidth = A4[0] - (PAGE_MARGINS * 2)
          const pxToPtRatio = 0.75

          pdfContent.images[`SRC:${element.props.src}`] = element.props.src.includes('http') ? element.props.src : `${baseUrl}${element.props.src}`
          return {
            image: `SRC:${element.props.src}`,
            width: element.props.width ? Math.min(element.props.width * pxToPtRatio, maxWidth) : maxWidth,
            style: 'img',
            headlineLevel
          }
        }

        if (element.tag === 'div' && element.props.dataType === 'columnBlock') {
          return {
            columns: element.children
              .filter(div => div.props.dataType === 'column')
              .map(col => ({
                stack: col.children.map(colChild => transformElementToContent(colChild))
              }))
          }
        }

        if (element.tag === 'table') {
          const tableRowElements = element.children[0].children
          const columnsCount = Math.max(...tableRowElements.map(row => row.children.length))

          const tableContent = {
            style: 'table',
            table: {
              headerRows: 1,
              widths: new Array(columnsCount).fill('auto'),
              body: tableRowElements.map(row => row.children.flatMap((cell) => {
                const cellContent = {
                  style: cell.tag, // th or td
                  rowSpan: Number(cell.props.rowSpan ?? 1),
                  colSpan: Number(cell.props.colSpan ?? 1),
                  stack: cell.children.map((cellChild, index) => {
                    const content = transformElementToContent(cellChild)
                    if (index === cell.children.length - 1) {
                      // remove the margin of the last element
                      content.margin = [0, 0, 0, 0]
                    }
                    return content
                  }),
                  borderColor: new Array(4).fill('#ced4da')
                }

                // insert empty cells for col spans
                return [cellContent, ...(new Array(cellContent.colSpan - 1).fill(''))]
              }))
            }
          }

          // insert empty cells for row spans
          const rows = tableContent.table.body
          rows.forEach((row, rowIndex) => {
            row.forEach((cell, cellIndex) => {
              if (cell.rowSpan > 1) {
                rows[rowIndex + 1].splice(cellIndex, 0, ...(new Array(cell.colSpan).fill('')))
              }
            })
          })

          return tableContent
        }

        return {
          stack: extractText(element.children),
          style: element.tag,
          headlineLevel
        }
      }

      const elements = []
      const elementsTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'img', 'div', 'table']
      // const textTags = ['strong', 'u', 'a']

      function pushElements (body, depth) {
        if (body?.children) {
          let text = { tag: 'p', children: [] }

          body.children.forEach((child) => {
            if (child.type === 'element') {
              if (elementsTags.includes(child.tag)) {
                if (/^h[1-6]$/.test(child.tag)) {
                  const headerLevel = Number(child.tag.charAt(1))
                  if (depth + 2 > headerLevel) {
                    child.tag = `h${Math.min(depth + 2, 6)}`
                  }
                }

                if (text.children.length) {
                  elements.push(text)
                  text = { tag: 'p', children: [] }
                }
                elements.push(child)
              } else {
                text.children.push(child)
              }
            } else {
              text.children.push(child.value)
            }
          })

          if (text.children.length) {
            elements.push(text)
          }
        }
      }

      function findBodies (children, depth) {
        children.forEach((child) => {
          if (depth === 0) {
            elements.push({
              tag: 'pageBreak',
              children: []
            })
          }

          elements.push({
            tag: `h${depth + 1}`,
            children: [
              {
                text: child.name,
                tocItem: true,
                tocMargin: [16 * depth, 0, 0, 0],
                tocStyle: 'a'
              }
            ]
          })

          if (child.body) { pushElements(child.body, depth) }
          if (child.children) { findBodies(child.children, depth + 1) }
        })
      }

      findBodies(roots, 0)

      elements.forEach((element, index) => {
        if (element.tag === 'pageBreak') {
          elements[index + 1].headlineLevel = 1
        }
        pdfContent.content.push(transformElementToContent(element))
      })

      await this.pdfFromContent(
        pdfContent,
        project ? `${project.doc_type} - ${project.name}` : this.getTitle(githubRef)
      )
    },
    getTitle (githubRef, project) {
      if (project) {
        return this.project.name
      }

      if (githubRef.startsWith('dept')) {
        return 'Trame départementale'
      }
      if (githubRef.startsWith('region')) {
        return 'Trame régionale'
      }
      if (githubRef === 'main') {
        return 'Trame nationale'
      }
    }
  }

  inject('pdf', pdfMaker)
}

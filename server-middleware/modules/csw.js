import axios from 'axios'
import { XMLParser, XMLBuilder } from 'fast-xml-parser'
import { getCommune, getIntercommunalite } from './geo'
import { and, or, intersects, polygon, propertyEquals } from './csw-filters'

const REGIONS_URLS = {
  'FR-BRE': {
    csw: 'https://geobretagne.fr/geonetwork/srv/fre/csw',
    record: 'https://geobretagne.fr/geonetwork/srv/fre/catalog.search#/metadata',
    categories: 'https://geobretagne.fr/geonetwork/srv/fre/qi?_content_type=json&summaryOnly=true'
  }
}

const GET_RECORDS_BODY = {
  'csw:GetRecords': {
    'csw:Query': {
      'csw:ElementSetName': 'full',
      '@_typeNames': 'csw:Record'
    },
    '@_xmlns:csw': 'http://www.opengis.net/cat/csw/2.0.2',
    '@_xmlns:gml': 'http://www.opengis.net/gml',
    '@_xmlns:ogc': 'http://www.opengis.net/ogc',
    '@_xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    '@_xmlns:ows': 'http://www.opengis.net/ows',
    '@_outputSchema': 'http://www.opengis.net/cat/csw/2.0.2',
    '@_outputFormat': 'application/xml',
    '@_version': '2.0.2',
    '@_service': 'CSW',
    '@_resultType': 'results',
    '@_startPosition': 1,
    '@_maxRecords': 100,
    '@_xsi:schemaLocation':
      'http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd'
  }
}

const parser = new XMLParser({ ignoreAttributes: false })
const builder = new XMLBuilder({ ignoreAttributes: false })

const cswClient = axios.create({
  headers: {
    'Content-Type': 'application/xml'
  },
  params: {
    request: 'GetRecords'
  },
  transformRequest: (data) => {
    return builder.build(data)
  },
  transformResponse: (data) => {
    return parser.parse(data)
  }
})

function cleanRecord (rawRecord) {
  let bbox
  if (rawRecord['ows:BoundingBox']) {
    const rawBbox = Array.isArray(rawRecord['ows:BoundingBox'])
      ? rawRecord['ows:BoundingBox'][0]
      : rawRecord['ows:BoundingBox']

    bbox = [
      rawBbox['ows:LowerCorner'].split(' ').reverse(),
      rawBbox['ows:UpperCorner'].split(' ').reverse()
    ]
  }

  let links = []
  if (rawRecord['dc:URI']) {
    links = Array.isArray(rawRecord['dc:URI']) ? rawRecord['dc:URI'] : [rawRecord['dc:URI']]
    links = links.map(link => ({
      url: link['#text'],
      protocol: link['@_protocol'],
      name: link['@_name'],
      description: link['@_description']
    }))
  }

  return {
    id: rawRecord['dc:identifier'],
    date: rawRecord['dc:date'],
    title: rawRecord['dc:title'],
    description: rawRecord['dc:description'],
    subjects: rawRecord['dc:subject'],
    source: rawRecord['dc:source'],
    bbox,
    links
  }
}

module.exports = {
  async getRecords (cswUrl, start = 1, max = 100, filter = undefined) {
    const body = { ...GET_RECORDS_BODY }
    body['csw:GetRecords']['@_startPosition'] = start
    body['csw:GetRecords']['@_maxRecords'] = max

    if (filter) {
      body['csw:GetRecords']['csw:Query']['csw:Constraint'] = {
        'ogc:Filter': filter,
        '@_version': '1.1.0'
      }
    }

    const { data } = await cswClient.post(cswUrl, body)
    const results = data['csw:GetRecordsResponse']['csw:SearchResults']

    return {
      records: Array.isArray(results['csw:Record'])
        ? results['csw:Record']
        : [results['csw:Record']],
      matched: Number(results['@_numberOfRecordsMatched']),
      returned: Number(results['@_numberOfRecordsReturned']),
      next: Number(results['@_nextRecord'])
    }
  },

  async getAllRecords (cswUrl, filter) {
    const firstRes = await this.getRecords(cswUrl, 1, 100, filter)

    let allRecords = [...firstRes.records]

    if (firstRes.matched > firstRes.returned) {
      const nextResPromises = []

      for (let i = firstRes.next; i < firstRes.matched; i += 100) {
        nextResPromises.push(this.getRecords(cswUrl, i, 100, filter))
      }

      const nextResRecords = (await Promise.all(nextResPromises)).flatMap(res => res.records)

      allRecords = allRecords.concat(nextResRecords)
    }

    return allRecords
  },

  async getData (codeInsee, isEpci, category) {
    const { region } = isEpci ? getIntercommunalite(codeInsee) : getCommune(codeInsee)
    const cswUrl = REGIONS_URLS[region.iso].csw

    if (!cswUrl) {
      return []
    }

    const contourRes = await axios.get(
      `https://geo.api.gouv.fr/${isEpci ? 'epcis' : 'communes'}/${codeInsee}?fields=nom,contour`
    )

    if (!['Polygon', 'MultiPolygon'].includes(contourRes.data.contour.type)) {
      throw new Error(
        'Unhandled geometry type : ' + contourRes.data.contour.type
      )
    }

    let coordinates = contourRes.data.contour.coordinates
    if (contourRes.data.contour.type === 'MultiPolygon') {
      coordinates = coordinates.flat()
    }

    const contours = coordinates.map(arr => arr.map(([lon, lat]) => [lat, lon]))

    const rawRecords = await this.getAllRecords(cswUrl,
      and(
        propertyEquals('Subject', category),
        contours.length === 1
          ? intersects(polygon(contours[0]))
          : or(
            ...contours.map(contour => intersects(polygon(contour)))
          )
      )
    )

    return rawRecords.map(cleanRecord).map((r) => {
      r.url = REGIONS_URLS[region.iso].record + '/' + r.id
      return r
    })
  },

  async getCategories (codeInsee, isEpci) {
    const { region } = isEpci ? getIntercommunalite(codeInsee) : getCommune(codeInsee)
    const categoriesUrl = REGIONS_URLS[region.iso].categories

    const { data } = await axios.get(categoriesUrl)

    return data[0].topicCats.map(topic => topic['@label']).filter(Boolean)
  }
}

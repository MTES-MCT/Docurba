export function propertyLike (propertyName, literal) {
  return {
    'ogc:PropertyIsLike': {
      'ogc:PropertyName': propertyName,
      'ogc:Literal': literal,
      '@_matchCase': 'false',
      '@_wildCard': '*',
      '@_singleChar': '_',
      '@_escapeChar': '\\'
    }
  }
}

export function propertyEquals (propertyName, literal) {
  return {
    'ogc:PropertyIsEqualTo': {
      'ogc:PropertyName': propertyName,
      'ogc:Literal': literal
    }
  }
}

export function search (literal) {
  return propertyLike('csw:AnyText', literal)
}

export function bbox (lowerCorner, upperCorner) {
  return {
    'ogc:BBOX': {
      'ogc:PropertyName': 'ows:BoundingBox',
      'gml:Envelope': {
        'gml:lowerCorner': `${lowerCorner[0]} ${lowerCorner[0]}`,
        'gml:upperCorner': `${upperCorner[0]} ${upperCorner[0]}`,
        '@_srsName': 'urn:ogc:def:crs:EPSG::4326'
      }
    }
  }
}

export function polygon (coordinates) {
  return {
    'gml:Polygon': {
      'gml:exterior': {
        'gml:LinearRing': {
          'gml:posList': coordinates
            .map(([lat, lng]) => `${lat} ${lng}`)
            .join(' ')
        }
      },
      '@_srsName': 'http://www.opengis.net/def/crs/EPSG/0/4326'
    }
  }
}

export function intersects (shape) {
  return {
    'ogc:Intersects': {
      'ogc:PropertyName': 'ows:BoundingBox',
      ...shape
    }
  }
}

export function within (shape) {
  return {
    'ogc:Within': {
      'ogc:PropertyName': 'ows:BoundingBox',
      ...shape
    }
  }
}

export function overlaps (shape) {
  return {
    'ogc:Overlaps': {
      'ogc:PropertyName': 'ows:BoundingBox',
      ...shape
    }
  }
}

export function agg (clause, ...filters) {
  let _agg = {}

  for (const filter of filters) {
    const key = Object.keys(filter)[0]

    if (_agg[key]) {
      if (Array.isArray(_agg[key])) {
        _agg[key].push({ ...filter[key] })
      } else {
        _agg[key] = [{ ..._agg[key] }, { ...filter[key] }]
      }
    } else {
      _agg = {
        ..._agg,
        ...filter
      }
    }
  }

  return {
    [clause]: _agg
  }
}

export function and (...filters) {
  return agg('ogc:And', ...filters)
}

export function or (...filters) {
  return agg('ogc:Or', ...filters)
}

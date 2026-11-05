import axios from 'axios'
import { uniq } from 'lodash'

const githubAxios = axios.create({
  baseURL: `https://api.github.com/repos/${
    process.env.GITHUB_PAC_REPO_OWNER
  }/${
    process.env.GITHUB_PAC_REPO_NAME
  }`,
  headers: {
    Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
  },
})

export const state = () => ({
  contentByPath: {},
  contentByPathByDepartmentCode: {},
  contentByPathByRegionCode: {},
  frame: [],
  frameByDepartmentCode: {},
  frameByRegionCode: {},
})

export const getters = {}

export const mutations = {
  setContent(state, { content, path, ...params }) {
    if (params.departmentCode) {
      state.contentByPathByDepartmentCode = {
        ...state.contentByPathByDepartmentCode,
        [params.departmentCode]: {
          ...(state.contentByPathByDepartmentCode[params.departmentCode] || {}),
          [path]: content,
        },
      }
    } else if (params.regionCode) {
      state.contentByPathByRegionCode = {
        ...state.contentByPathByRegionCode,
        [params.regionCode]: {
          ...(state.contentByPathByRegionCode[params.regionCode] || {}),
          [path]: content,
        },
      }
    } else {
      state.contentByPath = {
        ...state.contentByPath,
        [path]: content,
      }
    }
  },
  setFrame(state, { frame, ...params }) {
    if (params.departmentCode) {
      state.frameByDepartmentCode = {
        ...state.frameByDepartmentCode,
        [params.departmentCode]: frame,
      }
    } else if (params.regionCode) {
      state.frameByRegionCode = {
        ...state.frameByRegionCode,
        [params.regionCode]: frame,
      }
    } else {
      state.frame = frame
    }
  },
}

export const actions = {
  async get({ commit, state }, params) {
    let ref = 'main'

    if (params.departmentCode) {
      if (params.departmentCode in state.frameByDepartmentCode) {
        return state.frameByDepartmentCode[params.departmentCode]
      }

      ref = _getRef('dept', params.departmentCode)
    } else if (params.regionCode) {
      if (params.regionCode in state.frameByRegionCode) {
        return state.frameByRegionCode[params.regionCode]
      }

      ref = _getRef('region', params.regionCode)
    }

    const { data } = await githubAxios.get(`/git/trees/${ref}?recursive=1`)
    const paths = data.tree
      .filter(({ path }) => path.startsWith('PAC') && path.endsWith('.md'))
      .map(({ path }) => path.slice(4))
    const frame = uniq(paths.map((path) => path.split('/')[0]))
      .map((path) => _getSection(path, paths))

    commit('setFrame', { frame, ...params })

    return frame
  },
  async getContent({ commit, state }, { path, ...params }) {
    let ref = 'main'

    if (params.departmentCode) {
      if (
        params.departmentCode in state.contentByPathByDepartmentCode
        && path in state.contentByPathByDepartmentCode[params.departmentCode]
      ) {
        return state.contentByPathByDepartmentCode[params.departmentCode][path]
      }

      ref = _getRef('dept', params.departmentCode)
    } else if (params.regionCode) {
      if (
        params.regionCode in state.contentByPathByRegionCode
        && path in state.contentByPathByRegionCode[params.regionCode]
      ) {
        return state.contentByPathByRegionCode[params.regionCode][path]
      }

      ref = _getRef('dept', params.regionCode)
    }

    let content = ''

    try {
      const { data } = await githubAxios.get(`/contents/${encodeURIComponent(`PAC/${
        path.endsWith('.md') ? path : `${path}/intro.md`
      }`)}?ref=${ref}`, {
        headers: {
          Accept: 'application/vnd.github.raw+json',
        },
      })
      content = data || ''
    } catch {
      // TODO :: Handle this
    }

    commit('setContent', { content, path, ...params })

    return content
  }
}

function _getRef(prefix, code) {
  const number = Number(code)

  return `${prefix}-${
    Number.isNaN(number)
      ? code
      : number
  }`
}

function _getSection(path, paths) {
  return {
    content: '',
    label: path.split('/').pop().replace('.md', ''),
    path,
    sections: uniq(
      paths.filter((p) => p.startsWith(`${path}/`) && !p.endsWith('intro.md'))
        .map((p) => `${path}/${p.slice(path.length + 1).split('/')[0]}`)
    ).map((p) => _getSection(p, paths)),
  }
}

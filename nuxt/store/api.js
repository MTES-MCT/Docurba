import axios from 'axios'
import { isArray } from 'lodash'
import qs from 'qs'
import { createClient } from '@supabase/supabase-js'

const djangoAxios = axios.create({
  baseURL: process.env.DJANGO_API_BASE_URL,
  paramsSerializer: params => qs.stringify(params, {
    arrayFormat: 'repeat',
    encode: false,
  }),
})
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

export const state = () => ({})

export const getters = {
  auth() {
    return supabase.auth
  },
  get(_state, getters) {
    async function get(path, params) {
      const { data } = await djangoAxios.get(path, {
        headers: getters.headers,
        params,
      })

      if (data.results === undefined) {
        return data
      }

      const results = [...data.results]

      if (data.num_pages > 1) {
        let nextUrl = data.next

        while (nextUrl !== null) {
          const { data: res } = await axios.get(nextUrl, {
            headers: getters.headers,
          })
          results.push(...res.results)
          nextUrl = res.next
        }
      }

      return results
    }

    return async (path, params) => {
      // Split key with more than 100 values in multiple queries
      const key = Object.keys(params).find((key) =>
        isArray(params[key]) && params[key].length > 100
      )

      if (!key) {
        return get(path, params)
      }

      const queries = []

      for (let i = 0; i < params[key].length; i += 100) {
        queries.push(get(path, {
          ...params,
          [key]: params[key].slice(i, i + 100),
        }))
      }

      return (await Promise.all(queries)).flat()
    }
  },
  getFromDatabase(_state, getters) {
    return (table, fields = ['*'], filters = []) =>
      getters.listFromDatabase(table, fields, filters).limit(1).single()
  },
  headers(_state, _getters, _rootState, rootGetters) {
    return rootGetters['auth/signedIn']
      ? { 'Supabase-Authorization': rootGetters['auth/user'].accessToken }
      : undefined
  },
  listFromDatabase() {
    return (table, fields = ['*'], filters = []) => {
      let query = supabase.from(table).select(fields.join())

      filters.forEach(([filter, field, value]) => {
        query = query[filter](field, value)
      })

      return query
    }
  },
}

export const mutations = {}

export const actions = {}

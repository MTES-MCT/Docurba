import { uniqueId } from 'lodash'

// interface Alert {
//   description: string | null
//   ellapsedDuration: number
//   id: string
//   startedAt: number
//   timeoutId: number
//   title: string | null
//   type: AlertType
// }
// enum AlertType {
//   Error = 'error',
//   Info = 'info',
//   Success = 'success',
//   Warning = 'warning',
// }

export const state = () => ({
  messages: [],
})

export const getters = {
  messages(state) {
    return state.messages
  },
}

export const mutations = {
  addMessage(state, message) {
    state.messages = [
      ...state.messages,
      message,
    ]

    return true
  },
  removeMessage(state, id) {
    const index = state.messages.findIndex(message => message.id === id)

    if (index === -1) {
      return false
    }

    state.messages = [
      ...state.messages.slice(0, index),
      ...state.messages.slice(index + 1),
    ]

    return true
  },
  setMessage(state, message) {
    const index = state.messages.findIndex(({ id }) => id === message.id)

    if (index === -1) {
      return false
    }

    state.messages = [
      ...state.messages.slice(0, index),
      message,
      ...state.messages.slice(index + 1),
    ]

    return true
  }
}

export const actions = {
  dismiss({ commit }, id) {
    return commit('removeMessage', id)
  },
  pause({ commit, state }, id) {
    const message = state.messages.find(message => message.id === id)
    const now = Date.now()

    if (!message) {
      return false
    }

    clearTimeout(message.timeoutId)

    commit('setMessage', {
      ...message,
      ellapsedDuration: message.ellapsedDuration + now - message.startedAt,
    })

    return true
  },
  restart({ commit, state }, id) {
    const message = state.messages.find(message => message.id === id)

    if (!message) {
      return false
    }

    const delay = 5000 - message.ellapsedDuration

    if (delay <= 0) {
      commit('removeMessage', id)

      return true
    }

    const timeoutId = setTimeout(() => {
      commit('removeMessage', id)
    }, delay)

    commit('setMessage', {
      ...message,
      startedAt: Date.now(),
      timeoutId: timeoutId,
    })

    return true
  },
  send ({ commit }, message) {
    const id = uniqueId()
    const messageOrDefault = typeof message === 'string'
      ? { description: message }
      : message
    const timeoutId = setTimeout(() => {
      commit('removeMessage', id)
    }, 5000)

    commit('addMessage', {
      ellapsedDuration: 0,
      description: messageOrDefault.description ?? null,
      id,
      startedAt: Date.now(),
      timeoutId,
      title: message.title ?? null,
      type: message.type ?? 'info'
    })

    return id
  },
  sendError({ dispatch }, message) {
    return dispatch('send', {
      ...(typeof message === 'string' ? { description: message } : message),
      type: 'error'
    })
  },
  sendInfo({ dispatch }, message) {
    return dispatch('send', {
      ...(typeof message === 'string' ? { description: message } : message),
      type: 'info'
    })
  },
  sendSuccess({ dispatch }, message) {
    return dispatch('send', {
      ...(typeof message === 'string' ? { description: message } : message),
      type: 'success'
    })
  },
  sendWarning({ dispatch }, message) {
    return dispatch('send', {
      ...(typeof message === 'string' ? { description: message } : message),
      type: 'warning'
    })
  },
}

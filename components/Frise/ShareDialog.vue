<template>
  <v-dialog v-model="dialog" width="800">
    <template #activator="{ on, attrs }">
      <v-btn v-bind="attrs" outlined color="primary" class="ml-2" v-on="on">
        Partager
      </v-btn>
    </template>

    <v-card max-height="450" class="overflow-auto">
      <div class="text-right pr-2 pt-2">
        <v-btn color="primary" text @click="dialog = false">
          Fermer x
        </v-btn>
      </div>
      <v-card-title class="text-h5 align-start pl-8">
        <div>Partager {{ documentName }}</div>
      </v-card-title>

      <v-card-text class="pt-4 px-5">
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-combobox
                ref="combobox"
                v-model="selectedCombobox"
                filled
                :items="suggestedCollabs"
                :filter="filter"
                multiple
                placeholder="Emails"
                validate-on-blur
              >
                <template #append>
                  <v-btn color="primary" depressed @click="clickShared">
                    Partager
                  </v-btn>
                </template>
                <template #item="{ item, on, attrs }">
                  <v-list-item v-bind="attrs" v-on="on">
                    <v-list-item-avatar :color="item.color" class="text-capitalize white--text font-weight-bold">
                      {{ item.avatar }}
                    </v-list-item-avatar>
                    <v-list-item-content>
                      <v-list-item-title class="text-capitalize">
                        {{ item.label }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        <span> {{ $utils.posteDetails(item.poste) }}</span>
                        <template v-if="item.detailsPoste">
                          <span
                            v-for="detail in item.detailsPoste"
                            :key="`colab-${item.email}-${detail}`"
                          >
                            {{ ', ' + $utils.posteDetails(detail) }}
                          </span>
                        </template>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </template>
                <template #selection="{ attrs, item, parent, selected }">
                  <v-chip
                    v-if="item === Object(item)"
                    v-bind="attrs"
                    :color="`${item.color} lighten-3`"
                    :input-value="selected"
                    label
                    small
                  >
                    <span class="pr-2">
                      {{ item.email }} <span v-if=" item.label">({{ item.label }})</span>
                    </span>
                    <v-icon
                      small
                      @click="parent.selectItem(item)"
                    >
                      $delete
                    </v-icon>
                  </v-chip>
                </template>
              </v-combobox>
            </v-col>
            <v-col cols="12">
              <div>
                Partagé avec:
              </div>
              <div>
                <v-list two-line>
                  <template v-for="(collaborator) in collaborators">
                    <v-list-item :key="collaborator.id" :value="collaborator">
                      <v-list-item-avatar :color="collaborator.color" class="text-capitalize white--text font-weight-bold">
                        {{ collaborator.avatar }}
                      </v-list-item-avatar>
                      <v-list-item-content>
                        <v-list-item-title class="text-capitalize">
                          {{ collaborator.label }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                          <span> {{ $utils.posteDetails(collaborator.poste) }}</span>
                          <template v-if="collaborator.detailsPoste">
                            <span v-for="detail in collaborator.detailsPoste" :key="`colab-${collaborator.email}-${detail}`">{{ ', ' + $utils.posteDetails(detail) }}</span>
                          </template>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                      <v-list-item-action>
                        <v-icon
                          color="grey lighten-1"
                        >
                          mdi-star-outline
                        </v-icon>

                        <v-menu v-if="!collaborator.legacy_sudocu && !collaborator.initiator">
                          <template #activator="{ on: onMenu, attrs: attrsMenu }">
                            <v-btn icon color="primary" v-bind="attrsMenu" v-on="onMenu">
                              <v-icon> {{ icons.mdiDotsVertical }}</v-icon>
                            </v-btn>
                          </template>
                          <v-list>
                            <v-list-item link>
                              <v-list-item-title class="error--text" @click="uninviteShared(collaborator)">
                                Retirer de la procédure
                              </v-list-item-title>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </v-list-item-action>
                    </v-list-item>
                  </template>
                </v-list>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
    <v-snackbar
      v-model="snackbar"
      top
      color="success"
      outlined
      min-width="800"
      :timeout="5000"
    >
      <v-icon small color="success" class="mr-2">
        {{ icons.mdiCheckCircle }}
      </v-icon>
      {{ snackText }}
    </v-snackbar>
  </v-dialog>
</template>
<script>
import { uniq } from 'lodash'
import { mdiDotsVertical, mdiCheckCircle } from '@mdi/js'

export default
{
  name: 'ShareDialog',
  props: {
    documentName: {
      type: String,
      required: true
    },
    collaborators: {
      type: Array,
      required: true
    },
    departement: {
      type: String,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      snackbar: false,
      snackText: '',
      dialog: false,
      collaboratorsItems: null,
      selectedCombobox: [],
      search: null,
      icons: {
        mdiDotsVertical,
        mdiCheckCircle
      }
    }
  },
  computed: {
    suggestedCollabs () {
      return this.collaboratorsItems?.filter(item =>
        !this.collaborators.some(collaborator => collaborator.email === item.email)
      ).map(e => ({ ...e, text: e.email })) ?? []
    }

  },
  watch: {
    selectedCombobox (val, prev) {
      if (val.length === prev.length) { return }

      this.selectedCombobox = val.map((v) => {
        if (typeof v === 'string') {
          v = {
            email: v
          }
        }
        return v
      })
    }
  },
  async mounted () {
    this.collaboratorsItems = await this.$sharing.getSuggestedCollaborators(this.collectivite)
  },
  methods: {
    uninviteShared (collaborator) {
      this.$emit('remove_shared', collaborator)
      this.snackbar = true
      this.snackText = ' Collaborateur supprimé.'
    },
    clickShared () {
      this.$refs.combobox.blur()
      const emailsList = [...this.selectedCombobox]

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

      if (emailRegex.test(this.$refs.combobox.searchInput)) {
        emailsList.push({ email: this.$refs.combobox.searchInput })
      }

      this.$emit('share_to', uniq(emailsList))
      this.snackbar = true
      this.snackText = 'Collaborateur ajouté.'
    },
    filter (item, queryText, itemText) {
      if (item.header) { return false }
      const hasValue = val => val != null ? val : ''

      const text = hasValue(item.label)
      const query = hasValue(queryText)
      return text?.toString()
        ?.toLowerCase()
        .includes(query.toString().toLowerCase())
    }
  }
}
</script>

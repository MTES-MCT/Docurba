<template>
  <v-dialog v-model="dialog" width="800">
    <template #activator="{ on, attrs }">
      <v-btn v-bind="attrs" outlined color="primary" v-on="on">
        Partager
      </v-btn>
    </template>

    <v-card>
      <v-card-title class="text-h5 d-flex flex-column">
        <div>
          fefg
        </div>
        <div>Partager</div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field filled placeholder="Email, séparés par une virgule">
                <template #append>
                  <v-btn color="primary" depressed>
                    Partager
                  </v-btn>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12">
              <div>
                Partagé avec:
              </div>
              <div>
                <v-list two-line>
                  <template v-for="(collaborator, index) in collaborators">
                    <v-list-item :key="collaborator.title + index">
                      <template>
                        <v-list-item-avatar color="primary" class="text-capitalize white--text font-weight-bold">
                          {{ collaborator.avatar }}
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>
                            {{ collaborator.title }}
                          </v-list-item-title>

                          <v-list-item-subtitle class="text--primary">
                            {{ collaborator.headline }}
                          </v-list-item-subtitle>
                        </v-list-item-content>

                        <v-list-item-action>
                          <v-icon
                            color="grey lighten-1"
                          >
                            mdi-star-outline
                          </v-icon>

                          <v-menu>
                            <template #activator="{ on: onMenu, attrs: attrsMenu }">
                              <v-btn icon color="primary" v-bind="attrsMenu" v-on="onMenu">
                                <v-icon> {{ icons.mdiDotsVertical }}</v-icon>
                              </v-btn>
                            </template>
                            <v-list>
                              <v-list-item link>
                                <v-list-item-title class="error--text">
                                  Retirer de la procédure
                                </v-list-item-title>
                              </v-list-item>
                            </v-list>
                          </v-menu>
                        </v-list-item-action>
                      </template>
                    </v-list-item>
                  </template>
                </v-list>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
    <!-- <v-snackbar
        :timeout="-1"
        :value="true"
        top
      >
        snackbar with <strong>Shaped</strong> property.
      </v-snackbar> -->
  </v-dialog>
</template>
<script>
import { mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'ShareDialog',
  data () {
    return {
      dialog: true,
      collaborators: [{ title: 'feverf', headline: ' lul', avatar: 'L' }],
      icons: {
        mdiDotsVertical
      }
    }
  },
  async mounted () {
    // const {
    //   data: collaborators,
    //   error: errorCollaborators
    // } = await this.$supabase.from('profiles').select('*').eq('departement', collectivite.departementCode)
    // this.collaborators = collaborators
  }
}
</script>

<template>
  <v-card class="tvwysiwyg-editor tiptap-content" flat outlined style="width: 100%;">
    <v-toolbar v-if="editor" ref="toolbar" flat>
      <v-toolbar-items>
        <v-btn depressed tile icon>
          <v-icon
            @click="
              editor
                .chain()
                .focus()
                .undo()
                .run()
            "
          >
            {{ icons.mdiUndo }}
          </v-icon>
        </v-btn>
        <v-btn depressed tile icon>
          <v-icon
            @click="
              editor
                .chain()
                .focus()
                .redo()
                .run()
            "
          >
            {{ icons.mdiRedo }}
          </v-icon>
        </v-btn>
        <v-select
          :value="typos[typos.length-1]"
          :items="typos"
          hide-details
          solo
          flat
          class="d-flex align-center typo-select"
          @change="changeTypo"
        >
          <template #item="{item}">
            <v-icon>{{ item.icon }}</v-icon>
          </template>
          <template #selection="{item}">
            <v-icon>{{ item.icon }}</v-icon>
          </template>
        </v-select>
        <v-menu v-if="dense">
          <template #activator="{on}">
            <v-btn icon tile depressed v-on="on">
              <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
            </v-btn>
          </template>
          <v-toolbar>
            <VTiptapItems :editor="editor" />
          </v-toolbar>
        </v-menu>
      </v-toolbar-items>
      <VTiptapItems v-if="!dense" :editor="editor" />
      <v-toolbar-items>
        <v-btn
          depressed
          tile
          class="linkBtn"
          icon
          @click="openLinkMenu"
        >
          <v-icon>{{ icons.mdiLink }}</v-icon>
        </v-btn>
        <v-tooltip
          :value="!selecitionValid"
          attach=".linkBtn"
          close-delay="3000"
        >
          Selectionnez du text pour ajouter un lien
        </v-tooltip>
        <v-btn
          depressed
          tile
          icon
          @click="$refs['imageFileInput'].click()"
        >
          <v-icon>{{ icons.mdiFileImage }}</v-icon>
        </v-btn>
        <input :ref="'imageFileInput'" class="d-none" type="file" @change="inputImage">
        <slot />
      </v-toolbar-items>
    </v-toolbar>
    <v-card-text
      id="VTipTap-TextArea"
      class="pb-1 pt-3 text-editor"
      @click="editor.chain().focus()"
      @drop.prevent="dropImage"
      @dragenter.prevent
      @dragover.prevent
    >
      <v-menu
        v-if="selection && selectionMenu"
        v-model="selectionMenu"
        :position-x="selectionMenuPosition.x"
        :position-y="selectionMenuPosition.y + 20"
        :close-on-click="false"
        :close-on-content-click="false"
      >
        <v-card>
          <v-text-field
            v-model="linkHref"
            :append-icon="icons.mdiCheck"
            hide-details=""
            filled
            label="ajouter un lien"
            @click:append="addLink"
          />
          <v-card-text v-if="links.length">
            <v-treeview
              hoverable
              open-on-click
              :items="links"
              item-text="titre"
              class="d-block text-truncate"
              item-key="path"
            >
              <template #label="{item}">
                <div class="d-block text-truncate" @click="addInternalLink(item)">
                  {{ item.titre }}
                </div>
              </template>
            </v-treeview>
          </v-card-text>
        </v-card>
      </v-menu>
      <editor-content v-if="!readonly" :editor="editor" />
      <nuxt-content v-else :document="readonlyBody" />
    </v-card-text>
  </v-card>
</template>
<script>
import { Editor, EditorContent } from '@tiptap/vue-2'
import StarterKit from '@tiptap/starter-kit'
import { Underline } from '@tiptap/extension-underline'
import { Link } from '@tiptap/extension-link'
import { Image } from '@tiptap/extension-image'

import { v4 as uuidv4 } from 'uuid'

import {
  mdiUndo, mdiRedo, mdiFormatHeader1, mdiFormatText,
  mdiFormatHeader2, mdiFormatHeader3, mdiFormatHeader4,
  mdiFormatBold, mdiFormatUnderline, mdiFormatItalic,
  mdiFormatListBulleted, mdiFormatListNumbered, mdiLink,
  mdiCheck, mdiFileImage, mdiDotsVertical
} from '@mdi/js'

export default {
  name: 'TvWYSIWYG',
  components: {
    EditorContent
  },
  props: {
    value: {
      // Can be plain string, HTML as string or JSON with content structure:
      // See: https://tiptap.dev/api/commands/set-content
      type: [String, Object],
      default: ''
    },
    links: {
      type: Array,
      default () { return [] }
    },
    depth: {
      type: Number,
      default: 0
    },
    readonly: {
      type: Boolean,
      default: false
    }
  },
  data () {
    Image.configure({
      allowBase64: true
    })

    return {
      editor: new Editor({
        extensions: [StarterKit, Underline, Link, Image],
        content: this.value,
        onUpdate: () => {
          this.$emit('input', this.editor.getHTML())
        }
      }),
      icons: {
        mdiUndo,
        mdiRedo,
        mdiFormatHeader1,
        mdiFormatBold,
        mdiFormatUnderline,
        mdiFormatItalic,
        mdiFormatListBulleted,
        mdiFormatListNumbered,
        mdiLink,
        mdiCheck,
        mdiFileImage,
        mdiDotsVertical
      },
      selecitionValid: true,
      selection: null,
      selectionMenu: false,
      selectionMenuPosition: {
        x: 0,
        y: 0
      },
      linkHref: '',
      dense: false
    }
  },
  computed: {
    typos () {
      const defaultTypos = [{
        icon: mdiFormatHeader4,
        value: 4
      }, {
        icon: mdiFormatText,
        value: 0
      }]

      return [{
        icon: mdiFormatHeader1,
        value: 1
      }, {
        icon: mdiFormatHeader2,
        value: 2
      }, {
        icon: mdiFormatHeader3,
        value: 3
      }].filter(t => t.value > this.depth).concat(defaultTypos)
    },
    readonlyBody () {
      return {
        body: this.$md.compile(this.value)
      }
    }
  },
  watch: {
    value (value) {
      const isSame = this.editor.getHTML() === value
      if (isSame) {
        return
      }

      this.editor.commands.setContent(value, false)
    }
  },
  mounted () {
    this.dense = this.$el.offsetWidth < 550

    const resizeObserver = new ResizeObserver(() => {
      this.dense = this.$el.offsetWidth < 550
    })

    resizeObserver.observe(this.$el)

    // Image.configure({
    //   allowBase64: true
    // })

    // this.editor = new Editor({
    //   extensions: [StarterKit, Underline, Link, Image],
    //   content: this.value,
    //   onUpdate: () => {
    //     this.$emit('input', this.editor.getHTML())
    //   }
    // })
  },
  beforeUnmount () {
    this.editor.destroy()
  },
  methods: {
    changeTypo (val) {
      this.editor.chain()
        .focus()
        .toggleHeading({ level: val })
        .run()
    },
    openLinkMenu () {
      this.selection = window.getSelection()

      if (!this.selection.anchorNode) {
        this.selecitionValid = false

        setTimeout(() => {
          this.selecitionValid = true
        }, 2500)
      }

      if (this.selectionMenu) {
        this.selectionMenu = false
      } else if (this.selection.type === 'Range') {
        this.selectionMenu = true

        this.linkHref = this.selection.anchorNode.parentElement.href

        const range = this.selection.getRangeAt(0)
        this.selectionMenuPosition = range.getBoundingClientRect()
      }
    },
    addInternalLink (link) {
      if (link && link.path) {
        // const projectPath = `/projets/${this.$route.params.projectId}/content`
        this.editor.commands.setLink({ href: `#${this.$PAC.pathToAnchor(link.path)}`, target: '_self' })
      }

      this.selectionMenu = false
    },
    addLink () {
      if (this.linkHref) {
        this.editor.commands.setLink({ href: this.linkHref, target: '_blank' })
        this.linkHref = ''
      } else {
        this.editor.commands.unsetLink()
      }

      this.selectionMenu = false
    },
    dropImage (dropEvent) {
      this.uploadImage(dropEvent.dataTransfer.files[0])
    },
    inputImage () {
      this.uploadImage(this.$refs.imageFileInput.files[0])
    },
    async  uploadImage (image) {
      if (image && image.type.includes('image')) {
        const { data } = await this.$supabase
          .storage
          .from('text-images')
          .upload(`public/${uuidv4()}.${image.name.split('.').pop()}`, image)

        this.editor.commands.setImage({
          src: `https://ixxbyuandbmplfnqtxyw.supabase.co/storage/v1/object/public/text-images/${data.path}`
        })

        // https://ixxbyuandbmplfnqtxyw.supabase.co/storage/v1/object/public/text-images/public/06a340d9-16be-4311-a8ff-30c68d416ce9.jpg?t=2022-12-08T15%3A38%3A26.939Z
        // https://ixxbyuandbmplfnqtxyw.supabase.co/storage/v1/object/public/text-images/public/809b5fe2-ccce-4380-9e7d-79c9cc9671d3.png
        // https://ixxbyuandbmplfnqtxyw.supabase.co/storage/v1/object/public-text/public/3cfc6b76-0d87-40f1-b160-77fd7bca4a9b.png
        // https://ixxbyuandbmplfnqtxyw.supabase.in/storage/v1/object/public-text/public/dda2b06f-e964-4d8a-af8c-49d8f55a4296.png
      }
    }
  }
}
</script>
<style scoped>
.tvwysiwyg-editor >>> .ProseMirror:focus {
  outline: none;
}

.text-editor {
  min-height: calc(100vh - 285px);
  max-height: calc(100vh - 285px);
  overflow: scroll;
}

.typo-select {
  width: 72px;
}
</style>

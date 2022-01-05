<template>
  <v-card class="tvwysiwyg-editor tiptap-content" style="width: 100%;">
    <v-toolbar v-if="editor">
      <v-toolbar-items>
        <v-btn icon>
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
        <v-btn icon>
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
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleHeading({ level: 1 })
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatHeader1 }}</v-icon>
        </v-btn>
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleBold()
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatBold }}</v-icon>
        </v-btn>
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleItalic()
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatItalic }}</v-icon>
        </v-btn>
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleUnderline()
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatUnderline }}</v-icon>
        </v-btn>
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleBulletList()
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatListBulleted }}</v-icon>
        </v-btn>
        <v-btn
          icon
          @click="
            editor
              .chain()
              .focus()
              .toggleOrderedList()
              .run()
          "
        >
          <v-icon>{{ icons.mdiFormatListNumbered }}</v-icon>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-card-text class="pb-1 pt-3 text-editor">
      <editor-content :editor="editor" />
    </v-card-text>
  </v-card>
</template>
<script>
import { Editor, EditorContent } from '@tiptap/vue-2'
import StarterKit from '@tiptap/starter-kit'
import { Underline } from '@tiptap/extension-underline'

import {
  mdiUndo, mdiRedo, mdiFormatHeader1,
  mdiFormatBold, mdiFormatUnderline, mdiFormatItalic,
  mdiFormatListBulleted, mdiFormatListNumbered
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
    }
  },
  data () {
    return {
      editor: null,
      icons: {
        mdiUndo,
        mdiRedo,
        mdiFormatHeader1,
        mdiFormatBold,
        mdiFormatUnderline,
        mdiFormatItalic,
        mdiFormatListBulleted,
        mdiFormatListNumbered
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
    this.editor = new Editor({
      extensions: [StarterKit, Underline],
      content: this.value,
      onUpdate: () => {
        this.$emit('input', this.editor.getHTML())
      }
    })
  },
  beforeUnmount () {
    this.editor.destroy()
  }
}
</script>
<style scoped>
.tvwysiwyg-editor >>> .ProseMirror:focus {
  outline: none;
}

.text-editor {
  min-height: calc(100vh - 250px);
  max-height: calc(100vh - 250px);
  overflow: scroll;
}
</style>

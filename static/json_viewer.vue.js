/* adapted from https://vuejs.org/v2/examples/tree-view.html */

let template = `
<li class="json_item">
  <div
    :class="[isFolder ? 'folder' : '']"
    @click="toggle">
    <span class="label">{{name}}:</span>
    <span v-if="isFolder" class="json_item">
    {{(isArray ? '[' : '{') + folderSize + (isOpen ? '-' : '+') + (isArray ? ']' : '}') }}
    </span>
    <span
      class="json_item"
      :class="itemType"
      v-else
      @click="$emit('item-picked', item)"
      >{{String(item)}}</span>
  </div>
  <ul v-show="isOpen" v-if="isOpen && itemType == 'object'">
    <json-item
      v-for="(entry, index) in Object.entries(item)"
      :key="entry[0]"
      :name="entry[0]"
      :item="entry[1]"
      @item-picked="$emit('item-picked', $event)"
    ></json-item>
  </ul>
  <ul v-show="isOpen" v-if="isOpen && itemType == 'array'">
    <json-item
      v-for="(subitem, index) in item"
      :key="index"
      :name="index"
      :item="subitem"
      @item-picked="$emit('item-picked', $event)"
    ></json-item>
  </ul>
</li>
`;

export const jsonItem = {
  name: "json-item",
  props: ["item", "name"],
  data: () => ({
    isOpen: false
  }),
  computed: {
    isFolder: function() {
      return this.isArray || this.isObject;
    },
    isArray: function() {
      return Array.isArray(this.item);
    },
    folderSize: function() {
      if (this.isArray) { return this.item.length }
      else if (this.isObject) { return Object.keys(this.item).length }
      else { return null }
    }, 
    isObject: function() {
      return (!this.isArray && this.item instanceof Object);
    },
    isNumber: function() {
      return (!this.isFolder && typeof(this.item) == "number")
    },
    isString: function() {
      return (!this.isFolder && typeof(this.item) == "string")
    },
    isNull: function() {
    },
    itemType: function() {
      if (this.isArray) { return "array" }
      else if (this.item == null) { return "null" }
      else if (this.isObject) { return "object" }
      else { return typeof(this.item) }
    },
    childItems: function() {
      if (this.isArray()) {
        return this.item;
      }
      else if (this.isObject) {
        return Object.entries(this.item)
      }
    }
  },
  methods: {
    toggle: function() {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    }
  },
  template
}

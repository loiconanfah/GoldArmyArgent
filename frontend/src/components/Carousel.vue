<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  autoPlay: {
    type: Boolean,
    default: true
  },
  interval: {
    type: Number,
    default: 5000
  }
})

const currentIndex = ref(0)
const container = ref(null)
let timer = null

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.items.length
}

const prev = () => {
  currentIndex.value = (currentIndex.value - 1 + props.items.length) % props.items.length
}

const startTimer = () => {
  if (props.autoPlay) {
    timer = setInterval(next, props.interval)
  }
}

const stopTimer = () => {
  if (timer) clearInterval(timer)
}

onMounted(startTimer)
onUnmounted(stopTimer)
</script>

<template>
  <div class="relative group" @mouseenter="stopTimer" @mouseleave="startTimer">
    <!-- Items -->
    <div class="overflow-hidden relative rounded-3xl">
      <div 
        class="flex transition-transform duration-700 ease-in-out" 
        :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
      >
        <div 
          v-for="(item, index) in items" 
          :key="index"
          class="w-full flex-shrink-0"
        >
          <slot :item="item" :index="index"></slot>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <button 
      @click="prev" 
      class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/5 backdrop-blur-md border border-white/10 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/10 z-20"
    >
      <ChevronLeftIcon class="w-6 h-6" />
    </button>
    <button 
      @click="next" 
      class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/5 backdrop-blur-md border border-white/10 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/10 z-20"
    >
      <ChevronRightIcon class="w-6 h-6" />
    </button>

    <!-- Indicators -->
    <div class="flex justify-center gap-2 mt-6">
      <button 
        v-for="(_, index) in items" 
        :key="index"
        @click="currentIndex = index"
        class="h-1.5 rounded-full transition-all duration-300"
        :class="currentIndex === index ? 'w-8 bg-violet-500' : 'w-2 bg-white/20'"
      ></button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue"

import type { AudioDetail } from "#shared/types/media"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"

import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"
import VLink from "~/components/VLink.vue"

const props = defineProps<{
  audio: AudioDetail
}>()
const { audio } = toRefs(props)
const { isHidden: shouldBlur } = useSensitiveMedia(audio)
</script>

<template>
  <div
    class="global-track grid w-full grid-cols-[3rem,1fr] grid-rows-[3rem,3rem] rounded ring-1 ring-[--color-gray-3] ring-opacity-20"
  >
    <div class="h-12 w-12 rounded-ss">
      <VAudioThumbnail class="rounded-ss" :audio="audio" />
    </div>

    <div class="flex h-12 items-center justify-between rounded-se bg-default">
      <VLink
        :href="`/audio/${audio.id}`"
        class="hover-underline label-bold z-10 flex flex-row items-center px-3 pe-12 text-default"
        :class="{ 'blur-text': shouldBlur }"
      >
        {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
      </VLink>
    </div>
    <slot
      name="audio-control"
      v-bind="{ size: 'medium', layout: 'global' } as const"
    />
    <slot name="controller" :usable-frac="1" />
  </div>
</template>

<style scoped>
.global-track .thumbnail {
  @apply h-12 w-12 rounded-ss;
}
.global-track .thumbnail img,
.global-track .thumbnail ~ svg {
  @apply rounded-ss;
}

.global-track .waveform {
  @apply h-full rounded-ee;
  --waveform-background-color: theme("backgroundColor.default");
}
.global-track .audio-control {
  @apply rounded-es;
}
</style>

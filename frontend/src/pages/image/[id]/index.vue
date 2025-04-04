<script setup lang="ts">
import {
  definePageMeta,
  showError,
  useAsyncData,
  useHead,
  useNuxtApp,
  useRoute,
} from "#imports"
import { computed, ref, watch } from "vue"

import axios from "axios"

import { IMAGE } from "#shared/constants/media"
import { skipToContentTargetId } from "#shared/constants/window"
import { firstParam, validateUUID } from "#shared/utils/query-utils"
import { handledClientSide } from "#shared/utils/errors"
import type { ImageDetail } from "#shared/types/media"
import singleResultMiddleware from "~/middleware/single-result"
import { useSingleResultStore } from "~/stores/media/single-result"
import { useAnalytics } from "~/composables/use-analytics"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { useSingleResultPageMeta } from "~/composables/use-single-result-page-meta"
import { usePageRobotsRule } from "~/composables/use-page-robots-rule"
import { useRouteResultParams } from "~/composables/use-route-result-params"

import VBone from "~/components/VSkeleton/VBone.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedMedia from "~/components/VMediaInfo/VRelatedMedia.vue"
import VSketchFabViewer from "~/components/VSketchFabViewer.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VSingleResultControls from "~/components/VSingleResultControls.vue"
import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"
import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"
import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

defineOptions({
  name: "ImageDetailPage",
})

definePageMeta({
  layout: "content-layout",
  middleware: singleResultMiddleware,
})

usePageRobotsRule("single-result")

const singleResultStore = useSingleResultStore()

const nuxtApp = useNuxtApp()

const route = useRoute()
const mediaId = computed(() => firstParam(route?.params.id))

if (!mediaId.value || !validateUUID(mediaId.value)) {
  showError({
    statusCode: 404,
    message: `Invalid image id: "${mediaId.value}" on ${route?.fullPath}.`,
    fatal: true,
  })
}

const image = ref<ImageDetail | null>(
  singleResultStore.image?.id &&
    mediaId.value &&
    singleResultStore.image.id === mediaId.value
    ? singleResultStore.image
    : null
)
const fetchingError = computed(() => singleResultStore.fetchState.error)
const isLoadingOnClient = computed(
  () => !(import.meta.server || nuxtApp.isHydrating)
)

/**
 * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
 * and replace it with the provider image once the thumbnail is loaded.
 */
const imageSrc = ref(
  isLoadingOnClient.value ? image.value?.thumbnail : image.value?.url
)

/**
 * On the server and when hydrating the server-rendered page,
 * we directly load the main image, without loading the thumbnail first.
 * This is only `true` on the client navigation, where loading the thumbnail first
 * improves the perceived performance.
 */
const isLoadingThumbnail = ref(!(import.meta.server || nuxtApp.isHydrating))

const showLoadingState = computed(() => {
  if (sketchFabUid.value) {
    return false
  }
  return isLoadingThumbnail.value
})

const { sendCustomEvent } = useAnalytics()

const { resultParams } = useRouteResultParams()

const handleRightClick = () => {
  sendCustomEvent("RIGHT_CLICK_IMAGE", resultParams.value)
}

const { reveal, isHidden } = useSensitiveMedia(image.value)

const { pageTitle, detailPageMeta } = useSingleResultPageMeta(image)

useHead(() => ({
  ...detailPageMeta,
  title: pageTitle.value,
}))

const isLoadingMainImage = ref(true)
const sketchFabfailure = ref(false)

const sketchFabUid = computed(() => {
  if (image.value?.source !== "sketchfab" || sketchFabfailure.value) {
    return null
  }
  return image.value.url
    .split("https://media.sketchfab.com/models/")[1]
    .split("/")[0]
})

/**
 * On image error, fall back on image thumbnail or the error image.
 * @param event - image load error event.
 */
const onImageError = (event: Event) => {
  if (!(event.target instanceof HTMLImageElement)) {
    return
  }
  imageSrc.value =
    event.target.src === image.value?.url ? image.value.thumbnail : errorImage
}
/**
 * When the load event is fired for the thumbnail image, we set the dimensions
 * of the image, and replace the image src attribute with the `image.url`
 * to load the original provider image.
 * @param event - the image load event.
 */
const onImageLoaded = (event: Event) => {
  if (!(event.target instanceof HTMLImageElement) || !image.value) {
    return
  }

  isLoadingThumbnail.value = false

  if (isLoadingMainImage.value) {
    const dimensions = {
      width: event.target.naturalWidth,
      height: event.target.naturalHeight,
    }
    if (singleResultStore.mediaItem?.frontendMediaType === IMAGE) {
      singleResultStore.mediaItem.width = dimensions.width
      singleResultStore.mediaItem.height = dimensions.height
    }
    if (!image.value.filetype) {
      axios
        .head(image.value.url)
        .then((res) => {
          const imageType = res.headers["content-type"]
          if (singleResultStore.mediaItem) {
            singleResultStore.mediaItem.filetype = imageType
          }
        })
        .catch(() => {
          /**
           * Do nothing. This avoids the console warning "Uncaught (in promise) Error:
           * Network Error" in Firefox in development mode.
           */
        })
    }

    imageSrc.value = image.value.url
    isLoadingMainImage.value = false
  }
}

const fetchImage = async () => {
  if (nuxtApp.isHydrating) {
    return image.value
  }

  const fetchedImage = await singleResultStore.fetch(IMAGE, mediaId.value)
  if (fetchedImage) {
    image.value = fetchedImage
    imageSrc.value = fetchedImage.thumbnail
    return fetchedImage
  }
  throw new Error(`Could not fetch image with id ${mediaId.value}`)
}

const { error } = await useAsyncData(
  "single-image-result",
  async () => {
    return await fetchImage()
  },
  { lazy: true, server: false }
)

const handleError = (error: Error) => {
  if (["Image not found", "Image ID not found"].includes(error.message)) {
    showError({
      statusCode: 404,
      message: "Image ID not found",
      fatal: true,
    })
  }
  if (fetchingError.value && !handledClientSide(fetchingError.value)) {
    showError({
      ...(fetchingError.value ?? {}),
      fatal: true,
    })
  }
}

if (error.value) {
  handleError(error.value)
}
watch(error, (err) => {
  if (err) {
    handleError(err)
  }
})
</script>

<template>
  <main :id="skipToContentTargetId" tabindex="-1" class="relative flex-grow">
    <VErrorSection
      v-if="fetchingError"
      :fetching-error="fetchingError"
      class="px-6 py-10 lg:px-10"
    />
    <template v-else-if="image">
      <VSafetyWall v-if="isHidden" v-bind="image" @reveal="reveal" />
      <template v-else>
        <VSingleResultControls :media="image" />
        <figure
          class="relative mb-4 grid grid-cols-1 grid-rows-1 justify-items-center border-b border-default px-6"
        >
          <VBone
            v-if="showLoadingState"
            class="col-span-full row-span-full h-[500px] w-[500px] self-center"
          />
          <!--
            re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906
            Note: this one, I believe, should remain disabled ; but should be double checked by the issue nonetheless
          -->
          <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
          <img
            v-if="!sketchFabUid"
            id="main-image"
            :src="imageSrc"
            :alt="image.title"
            class="col-span-full row-span-full h-full max-h-[500px] w-full rounded-se-sm rounded-ss-sm object-contain"
            :width="image.width ?? 0"
            :height="image.height ?? 0"
            @load="onImageLoaded"
            @error="onImageError"
            @contextmenu="handleRightClick"
          />
          <div
            v-if="sketchFabUid"
            class="col-span-full row-span-full w-full lg:max-w-4xl lg:px-4"
          >
            <VSketchFabViewer
              :uid="sketchFabUid"
              class="rounded-se-sm rounded-ss-sm"
              @failure="sketchFabfailure = true"
            />
          </div>
        </figure>

        <section
          class="grid grid-cols-1 grid-rows-[auto,1fr] sm:grid-cols-[1fr,auto] sm:grid-rows-1 sm:gap-x-6"
        >
          <VMediaInfo :media="image" class="min-w-0 sm:col-start-1" />
          <VGetMediaButton
            :media="image"
            media-type="image"
            class="row-start-1 mb-4 !w-full flex-initial sm:col-start-2 sm:mb-0 sm:mt-1 sm:!w-auto"
          />
        </section>

        <VMediaReuse :media="image" />
        <VMediaDetails :media="image" />

        <VRelatedMedia v-if="image" media-type="image" :related-to="image.id" />
      </template>
    </template>
    <VBone
      v-else-if="showLoadingState"
      class="col-span-full row-span-full mx-auto h-[500px] w-[500px]"
    />
  </main>
</template>

<style scoped>
section {
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-12 lg:mx-auto lg:px-16;
}
</style>

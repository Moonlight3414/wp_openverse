import { useWindowSize, watchThrottled } from "@vueuse/core"

import type { Breakpoint } from "~/constants/screens"
import { ALL_SCREEN_SIZES } from "~/constants/screens"
import { useUiStore } from "~/stores/ui"

const widthToBreakpoint = (width: number): Breakpoint => {
  const bp = Object.entries(ALL_SCREEN_SIZES).find(
    ([, bpWidth]) => width >= bpWidth
  ) ?? ["xs", 0]
  return bp[0] as Breakpoint
}

/**
 * This composable updates the UI store when the screen width changes or
 * when the SSR layout settings are different from the cookie settings.
 */
export function useLayout() {
  const uiStore = useUiStore()

  const { width, height } = useWindowSize()

  const updateBreakpoint = () => {
    uiStore.updateBreakpoint(
      width.value,
      height.value,
      widthToBreakpoint(width.value)
    )
  }

  watchThrottled(
    [width, height],
    ([newWidth, newHeight]) => {
      const newBp = widthToBreakpoint(newWidth)
      uiStore.updateBreakpoint(newWidth, newHeight, newBp)
    },
    { throttle: 100 }
  )

  return {
    updateBreakpoint,
  }
}

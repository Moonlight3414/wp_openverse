import { useContext } from "@nuxtjs/composition-api"

/**
 * This wrapper around the plugin, retained to reduce code churn.
 * @see Refer to frontend/src/plugins/analytics.ts for plugin implementation
 *
 * @deprecated For new code, use `$sendCustomEvent` from Nuxt context
 */
export const useAnalytics = () => {
  const { $sendCustomEvent } = useContext()

  return { sendCustomEvent: $sendCustomEvent }
}

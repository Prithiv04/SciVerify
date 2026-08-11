import { createBrowserRouter } from 'react-router-dom'
import RootLayout from '@/layouts/RootLayout'
import FoundationPlaceholder from '@/routes/FoundationPlaceholder'
import UiPreviewPage from '@/pages/UiPreviewPage'
import { ROUTES } from '@/constants'

export const router = createBrowserRouter([
  {
    path: ROUTES.HOME,
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <FoundationPlaceholder />,
      },
      {
        path: ROUTES.UI_PREVIEW,
        element: <UiPreviewPage />,
      },
    ],
  },
])

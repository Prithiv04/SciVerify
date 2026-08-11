import { createBrowserRouter } from 'react-router-dom'
import RootLayout from '@/layouts/RootLayout'
import FoundationPlaceholder from '@/routes/FoundationPlaceholder'
import { GuestRoute, ProtectedRoute } from '@/routes/ProtectedRoute'
import UiPreviewPage from '@/pages/UiPreviewPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import ForgotPasswordPage from '@/pages/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/ResetPasswordPage'
import AuthHomePage from '@/pages/AuthHomePage'
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
      {
        element: <GuestRoute />,
        children: [
          {
            path: 'login',
            element: <LoginPage />,
          },
          {
            path: 'register',
            element: <RegisterPage />,
          },
        ],
      },
      {
        path: 'forgot-password',
        element: <ForgotPasswordPage />,
      },
      {
        path: 'reset-password',
        element: <ResetPasswordPage />,
      },
      {
        path: 'app',
        element: <ProtectedRoute />,
        children: [
          {
            path: 'home',
            element: <AuthHomePage />,
          },
        ],
      },
    ],
  },
])

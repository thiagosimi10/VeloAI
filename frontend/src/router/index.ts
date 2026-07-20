import { createRouter, createWebHistory } from 'vue-router'

import { useAdminAuthStore } from '@/stores/adminAuth'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { layout: 'auth', requiresAuth: false },
    },
    {
      path: '/change-password',
      name: 'change-password',
      component: () => import('@/views/ChangePasswordView.vue'),
      meta: { layout: 'auth', requiresAuth: true },
    },
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
      meta: { layout: 'marketing', requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/customers',
      name: 'customers',
      component: () => import('@/views/customers/CustomersListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/customers/new',
      name: 'customers-new',
      component: () => import('@/views/customers/CustomerFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/customers/:id/edit',
      name: 'customers-edit',
      component: () => import('@/views/customers/CustomerFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/suppliers',
      name: 'suppliers',
      component: () => import('@/views/suppliers/SuppliersListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/suppliers/new',
      name: 'suppliers-new',
      component: () => import('@/views/suppliers/SupplierFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/suppliers/:id/edit',
      name: 'suppliers-edit',
      component: () => import('@/views/suppliers/SupplierFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/categories',
      name: 'categories',
      component: () => import('@/views/categories/CategoriesListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/categories/new',
      name: 'categories-new',
      component: () => import('@/views/categories/CategoryFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/categories/:id/edit',
      name: 'categories-edit',
      component: () => import('@/views/categories/CategoryFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/products',
      name: 'products',
      component: () => import('@/views/products/ProductsListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/products/new',
      name: 'products-new',
      component: () => import('@/views/products/ProductFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/products/:id/edit',
      name: 'products-edit',
      component: () => import('@/views/products/ProductFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/products/:id/stock',
      name: 'products-stock',
      component: () => import('@/views/products/ProductStockView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/services',
      name: 'services',
      component: () => import('@/views/services/ServicesListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/services/new',
      name: 'services-new',
      component: () => import('@/views/services/ServiceFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/services/:id/edit',
      name: 'services-edit',
      component: () => import('@/views/services/ServiceFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/service-orders',
      name: 'service-orders',
      component: () => import('@/views/serviceOrders/ServiceOrdersListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/service-orders/new',
      name: 'service-orders-new',
      component: () => import('@/views/serviceOrders/ServiceOrderFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/service-orders/:id',
      name: 'service-orders-detail',
      component: () => import('@/views/serviceOrders/ServiceOrderDetailView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/sales',
      name: 'sales',
      component: () => import('@/views/sales/SalesListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/sales/new',
      name: 'sales-new',
      component: () => import('@/views/sales/SaleFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/sales/:id',
      name: 'sales-detail',
      component: () => import('@/views/sales/SaleDetailView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-receivable',
      name: 'accounts-receivable',
      component: () => import('@/views/finance/AccountsReceivableListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-receivable/new',
      name: 'accounts-receivable-new',
      component: () => import('@/views/finance/AccountReceivableFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-receivable/:id',
      name: 'accounts-receivable-detail',
      component: () => import('@/views/finance/AccountReceivableDetailView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-payable',
      name: 'accounts-payable',
      component: () => import('@/views/finance/AccountsPayableListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-payable/new',
      name: 'accounts-payable-new',
      component: () => import('@/views/finance/AccountPayableFormView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/accounts-payable/:id',
      name: 'accounts-payable-detail',
      component: () => import('@/views/finance/AccountPayableDetailView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/cash-flow',
      name: 'cash-flow',
      component: () => import('@/views/finance/CashFlowView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: () => import('@/views/knowledge/KnowledgeListView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/billing',
      name: 'billing',
      component: () => import('@/views/BillingView.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLoginView.vue'),
      meta: { layout: 'auth', requiresAdminAuth: false },
    },
    {
      path: '/admin/tenants',
      name: 'admin-tenants',
      component: () => import('@/views/admin/AdminTenantsView.vue'),
      meta: { layout: 'admin', requiresAdminAuth: true },
    },
    {
      path: '/admin/tenants/new',
      name: 'admin-tenants-new',
      component: () => import('@/views/admin/AdminTenantFormView.vue'),
      meta: { layout: 'admin', requiresAdminAuth: true },
    },
    {
      path: '/admin/tenants/:id/edit',
      name: 'admin-tenants-edit',
      component: () => import('@/views/admin/AdminTenantFormView.vue'),
      meta: { layout: 'admin', requiresAdminAuth: true },
    },
    {
      path: '/admin/tenants/:id/audit-log',
      name: 'admin-tenant-audit-log',
      component: () => import('@/views/admin/AdminTenantAuditLogView.vue'),
      meta: { layout: 'admin', requiresAdminAuth: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { layout: 'auth', requiresAuth: false },
    },
  ],
})

router.beforeEach(async (to) => {
  // Guard do Painel Administrativo (Fase 18) — completamente isolado do guard de
  // sessão de tenant abaixo. Um Platform Admin nunca compartilha estado/cookie com um
  // usuário de tenant, então a sessão é resolvida por um store separado.
  if (to.path.startsWith('/admin')) {
    const adminAuthStore = useAdminAuthStore()

    if (!adminAuthStore.isBootstrapped) {
      await adminAuthStore.fetchCurrentAdmin()
    }

    if (to.meta.requiresAdminAuth && !adminAuthStore.isAuthenticated) {
      return { name: 'admin-login' }
    }

    if (to.name === 'admin-login' && adminAuthStore.isAuthenticated) {
      return { name: 'admin-tenants' }
    }

    return true
  }

  const authStore = useAuthStore()

  // Restaura a sessão a partir do cookie HttpOnly uma única vez por carregamento da
  // aplicação (o estado do Pinia é perdido a cada reload de página).
  if (!authStore.isBootstrapped) {
    await authStore.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (
    authStore.isAuthenticated &&
    authStore.user?.mustChangePassword &&
    to.name !== 'change-password'
  ) {
    return { name: 'change-password' }
  }

  return true
})

export default router

import {
  Home as HomeIcon,
  BarChartOutlined as DashboardIcon,
  Public as PublicIcon,
  MonitorHeart as HealthIcon,
  PublicOff as PrivateIcon,
  AccountBoxRounded as UserIcon,
  SettingsOutlined as SettingsIcon,
  ListAlt as ListIcon,
  CreditCard as BillingIcon
} from '@mui/icons-material';

import { Home } from '../pages/Home';

import { Dashboard } from '../pages/Dashboard';

import { Route } from '../types/Route';

const routes: Array<Route> = [
  {
    key: 'router-home',
    title: 'Home',
    description: 'Home',
    component: Home,
    path: '/',
    isEnabled: true,
    icon: HomeIcon,
    appendDivider: true
  },
  {
    key: 'router-dashboard',
    title: 'Dashboard',
    description: 'Dashboard',
    component: Dashboard,
    path: '/dashboard',
    isEnabled: true,
    icon: DashboardIcon
  },
  {
    key: 'router-search',
    title: 'Search',
    description: 'Search',
    isEnabled: true,
    icon: HealthIcon,
    subRoutes: [
      {
        key: 'router-search-auth',
        title: 'Authors',
        description: 'Authors',
        path: '/search/authors',
        isEnabled: false,
        icon: PublicIcon
      },
      {
        key: 'router-search-institutions',
        title: 'Search institutions',
        description: 'Institutions',
        path: '/search/institutions',
        isEnabled: false,
        icon: PrivateIcon
      }
    ],
    appendDivider: true
  },
  {
    key: 'router-my-account',
    title: 'My Account',
    description: 'My Account',
    path: '/account',
    isEnabled: true,
    icon: UserIcon,
    subRoutes: [
      {
        key: 'router-settings',
        title: 'Settings',
        description: 'Account Settings',
        path: '/account/settings',
        isEnabled: true,
        icon: SettingsIcon
      },
      {
        key: 'router-preferences',
        title: 'Preferences',
        description: 'Account Preferences',
        path: '/account/preferences',
        isEnabled: true,
        icon: ListIcon
      },
      {
        key: 'router-billing',
        title: 'Billing',
        description: 'Account Billing',
        path: '/account/billing',
        isEnabled: true,
        icon: BillingIcon
      }
    ]
  }
];

export default routes;

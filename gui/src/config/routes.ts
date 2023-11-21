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

import { Arxiv } from 'pages/Microservices/Arxiv';
import { Database } from 'pages/Microservices/Database';
import { Home } from 'pages/Home';
import { Dashboard } from 'pages/Dashboard';
import { Users } from 'pages/Admin/Users';

import { Route } from '../types';
import { Patterns } from 'pages/Researcher/Patterns';
import { Projects } from 'pages/Researcher/Projects';


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
    key: 'router-microservices',
    title: 'microservices',
    description: 'Micorservices interfaces',
    isEnabled: true,
    icon: HealthIcon,
    subRoutes: [
      {
        key: 'router-microservices-arxiv',
        title: 'Arxiv',
        description: 'Arxiv interface',
        component: Arxiv,
        path: '/microservices/arxiv',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-microservices-core',
        title: 'Core',
        description: 'Core interface',
        path: '/microservices/core',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-microservices-metapub',
        title: 'Metapub',
        description: 'Pubmed interface',
        path: '/microservices/metapub',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-microservices-preprocessing',
        title: 'Preprocessing',
        description: 'Preprocessing microservices',
        path: '/microservices/preprocessing',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-microservices-database',
        title: 'Database',
        description: 'Database microservices',
        component: Database,
        path: '/microservices/database',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-microservices-orchestrator',
        title: 'Orchestrator',
        description: 'Orchestrator microservices',
        path: '/microservices/orchestrator',
        isEnabled: true,
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
    ]
  },
  {
    key: 'router-user',
    title: 'User',
    description: 'User interface',
    isEnabled: true,
    icon: HealthIcon,
    subRoutes: [
      {
        key: 'router-user-query',
        title: 'Query',
        description: 'Query interface',
        path: '/user/query',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-user-report',
        title: 'Report',
        description: 'Report interface',
        path: '/user/report',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-user-historic',
        title: 'Historic',
        description: 'Historic interface',
        path: '/user/historic',
        isEnabled: true,
        icon: PublicIcon
      }
    ]
  },
  {
    key: 'router-researcher',
    title: 'Researcher',
    description: 'Researcher interfaces',
    isEnabled: true,
    icon: HealthIcon,
    subRoutes: [
      {
        key: 'router-researcher-projects',
        title: 'Projects',
        description: 'Projects interface',
        component: Projects,
        path: '/researcher/projects',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-researcher-patterns',
        title: 'Patterns',
        description: 'Patterns interface',
        component: Patterns,
        path: '/researcher/patterns',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-researcher-pipelines',
        title: 'Pipelines',
        description: 'Pipelines interface',
        path: '/researcher/pipelines',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-researcher-validate',
        title: 'Validate',
        description: 'Validate interface',
        path: '/researcher/validate',
        isEnabled: true,
        icon: PublicIcon
      }
    ]
  },
  {
    key: 'router-admin',
    title: 'Admin',
    description: 'Admin interfaces',
    isEnabled: true,
    icon: HealthIcon,
    subRoutes: [
      {
        key: 'router-admin-users',
        title: 'Users',
        description: 'Users management',
        component: Users,
        path: '/admin/users',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-admin-setup',
        title: 'Setup',
        description: 'System setup',
        path: '/admin/setup',
        isEnabled: true,
        icon: PublicIcon
      },
      {
        key: 'router-admin-usage',
        title: 'Usage',
        description: 'Usage reports',
        path: '/admin/usage',
        isEnabled: true,
        icon: PublicIcon
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

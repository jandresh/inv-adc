import {
  Home as HomeIcon,
  InsightsOutlined as DashboardIcon,
  IntegrationInstructions as MicroservicesIcon,
  DnsOutlined as DatabaseIcon,
  AutoFixHigh as PreprocessingIcon,
  DescriptionOutlined as AcademicIcon,
  SearchOutlined as QueryIcon,
  SummarizeOutlined as ReportIcon,
  History as HistoricIcon,
  FolderOpenOutlined as ProjectsIcon,
  GridViewOutlined as PatternsIcon,
  CompareArrowsOutlined as PipelinesIcon,
  CheckCircleOutlined as ValidateIcon,
  GroupOutlined as UsersManagementIcon,
  AdminPanelSettingsOutlined as AdminIcon,
  ManageAccountsOutlined as AccountAdminIcon,
  BuildOutlined as SetupIcon,
  Timeline as UsageIcon,
  AccountBoxRounded as UserIcon,
  SettingsOutlined as SettingsIcon,
  TuneOutlined as PreferencesIcon,
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
import { Pipelines } from 'pages/Researcher/Pipelines';
import { Report } from 'pages/User/Report';

const routes: Array<Route> = [
  {
    key: 'router-home',
    title: 'Home',
    description: 'Home',
    component: Home,
    path: '/',
    isEnabled: true,
    icon: HomeIcon,
    appendDivider: true,
    allowedRoles: ['admin', 'guest', 'researcher', 'user']
  },
  {
    key: 'router-dashboard',
    title: 'Dashboard',
    description: 'Dashboard',
    component: Dashboard,
    path: '/dashboard',
    isEnabled: true,
    icon: DashboardIcon,
    allowedRoles: ['admin']
  },
  {
    key: 'router-microservices',
    title: 'Microservices',
    description: 'Microservices interfaces',
    isEnabled: true,
    icon: MicroservicesIcon,
    allowedRoles: ['admin', 'researcher'],
    subRoutes: [
      {
        key: 'router-microservices-arxiv',
        title: 'Arxiv',
        description: 'Arxiv interface',
        component: Arxiv,
        path: '/microservices/arxiv',
        isEnabled: false,
        icon: AcademicIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-microservices-core',
        title: 'Core',
        description: 'Core interface',
        path: '/microservices/core',
        isEnabled: false,
        icon: AcademicIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-microservices-metapub',
        title: 'Metapub',
        description: 'Pubmed interface',
        path: '/microservices/metapub',
        isEnabled: false,
        icon: AcademicIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-microservices-preprocessing',
        title: 'Preprocessing',
        description: 'Preprocessing microservices',
        path: '/microservices/preprocessing',
        isEnabled: false,
        icon: PreprocessingIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-microservices-database',
        title: 'Database',
        description: 'Database microservices',
        component: Database,
        path: '/microservices/database',
        isEnabled: true,
        icon: DatabaseIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-microservices-orchestrator',
        title: 'Orchestrator',
        description: 'Orchestrator microservices',
        path: '/microservices/orchestrator',
        isEnabled: false,
        icon: DatabaseIcon,
        allowedRoles: ['admin']
      }
    ]
  },
  {
    key: 'router-user',
    title: 'User',
    description: 'User interface',
    isEnabled: true,
    icon: UserIcon,
    allowedRoles: ['admin', 'researcher', 'user'],
    subRoutes: [
      {
        key: 'router-user-query',
        title: 'Query',
        description: 'Query interface',
        path: '/user/query',
        isEnabled: false,
        icon: QueryIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-user-report',
        title: 'Report',
        description: 'Report interface',
        component: Report,
        path: '/user/report',
        isEnabled: true,
        icon: ReportIcon,
        allowedRoles: ['admin', 'researcher', 'user']
      },
      {
        key: 'router-user-historic',
        title: 'Historic',
        description: 'Historic interface',
        path: '/user/historic',
        isEnabled: false,
        icon: HistoricIcon,
        allowedRoles: ['admin']
      }
    ]
  },
  {
    key: 'router-researcher',
    title: 'Researcher',
    description: 'Researcher interfaces',
    isEnabled: true,
    icon: UserIcon,
    allowedRoles: ['admin', 'researcher'],
    subRoutes: [
      {
        key: 'router-researcher-projects',
        title: 'Projects',
        description: 'Projects interface',
        component: Projects,
        path: '/researcher/projects',
        isEnabled: true,
        icon: ProjectsIcon,
        allowedRoles: ['admin', 'researcher']
      },
      {
        key: 'router-researcher-patterns',
        title: 'Patterns',
        description: 'Patterns interface',
        component: Patterns,
        path: '/researcher/patterns',
        isEnabled: true,
        icon: PatternsIcon,
        allowedRoles: ['admin', 'researcher']
      },
      {
        key: 'router-researcher-pipelines',
        title: 'Pipelines',
        description: 'Pipelines interface',
        component: Pipelines,
        path: '/researcher/pipelines',
        isEnabled: true,
        icon: PipelinesIcon,
        allowedRoles: ['admin', 'researcher']
      },
      {
        key: 'router-researcher-validate',
        title: 'Validate',
        description: 'Validate interface',
        path: '/researcher/validate',
        isEnabled: false,
        icon: ValidateIcon,
        allowedRoles: ['admin', 'researcher']
      }
    ]
  },
  {
    key: 'router-admin',
    title: 'Admin',
    description: 'Admin interfaces',
    isEnabled: true,
    icon: AdminIcon,
    allowedRoles: ['admin'],
    subRoutes: [
      {
        key: 'router-admin-users',
        title: 'Users',
        description: 'Users management',
        component: Users,
        path: '/admin/users',
        isEnabled: true,
        icon: UsersManagementIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-admin-setup',
        title: 'Setup',
        description: 'System setup',
        path: '/admin/setup',
        isEnabled: true,
        icon: SetupIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-admin-usage',
        title: 'Usage',
        description: 'Usage reports',
        path: '/admin/usage',
        isEnabled: true,
        icon: UsageIcon,
        allowedRoles: ['admin']
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
    icon: AccountAdminIcon,
    allowedRoles: ['admin', 'researcher', 'user'],
    subRoutes: [
      {
        key: 'router-settings',
        title: 'Settings',
        description: 'Account Settings',
        path: '/',
        isEnabled: true,
        icon: SettingsIcon,
        allowedRoles: ['admin', 'researcher', 'user']
      },
      {
        key: 'router-preferences',
        title: 'Preferences',
        description: 'Account Preferences',
        path: '/account/preferences',
        isEnabled: false,
        icon: PreferencesIcon,
        allowedRoles: ['admin']
      },
      {
        key: 'router-billing',
        title: 'Billing',
        description: 'Account Billing',
        path: '/account/billing',
        isEnabled: false,
        icon: BillingIcon,
        allowedRoles: ['admin']
      }
    ]
  }
];

export default routes;

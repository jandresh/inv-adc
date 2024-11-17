import { ComponentType, FC } from 'react';

interface Patterns {
  id: number;
  db: string;
  description: string;
  patternid: number;
  pattern: string;
}

type MenuItem = {
  id: number;
  name: string;
  description?: string;
  active: boolean;
};

type User = {
  id: string;
  orgId: string;
  firstName: string;
  lastName: string;
  email: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  isAdmin: boolean;
  isVerified: boolean;
  role: 'admin' | 'guest' | 'researcher' | 'user';
};

type Route = {
  key: string;
  title: string;
  description?: string;
  path?: string;
  component?: FC<{}>;
  isEnabled: boolean;
  icon?: ComponentType;
  subRoutes?: Route[];
  appendDivider?: boolean;
  expanded?: boolean;
  allowedRoles: Array<User['role']>;
};

export type { MenuItem, Patterns, Route, User };

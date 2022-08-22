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
};

type User = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  isAdmin: boolean;
  isVerified: boolean;
};

export type { MenuItem, Patterns, Route, User };

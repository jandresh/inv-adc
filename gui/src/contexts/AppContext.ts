import React, { createContext } from 'react';

import { User } from '../types';

export interface IAppContext {
  user: User;
  setUser: React.Dispatch<React.SetStateAction<User>>;
}

export const guestUser: User = {
  id: '',
  orgId: '',
  firstName: 'guest',
  lastName: '',
  email: '',
  createdAt: new Date(),
  updatedAt: new Date(),
  isActive: false,
  isAdmin: false,
  isVerified: false,
  role: 'guest'
};

export const AppContext = createContext<IAppContext>({
  user: guestUser,
  setUser: () => {}
});

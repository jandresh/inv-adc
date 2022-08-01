import { IAppContext } from '../contexts/AppContext';

import { User } from '../types';

class AppClient implements IAppContext {
  user: User;

  /**
   * Creates an instance of AppClient.
   * @memberof AppClient
   */
  constructor() {
    this.user = {
      id: '0',
      name: 'guest',
      email: 'user@user.com',
      createdAt: new Date(),
      updatedAt: new Date(),
      isAdmin: false,
      isActive: false,
      isVerified: false
    };
  }
}

export default AppClient;

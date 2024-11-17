import { Divider, Menu, MenuItem } from '@mui/material';
import React, { useContext } from 'react';

import { Settings, Preferences, SignOut } from '../../Actions';
import { AppContext, guestUser } from 'contexts/AppContext';

interface DefaultMenuProps {
  isMenuOpen: boolean;
  handleMenuClose: () => void;
  anchorEl: HTMLElement | null;
}

export const DefaultMenu = ({
  isMenuOpen,
  handleMenuClose,
  anchorEl
}: DefaultMenuProps) => {
  const context = useContext(AppContext);
  return (
    <Menu
      anchorEl={anchorEl}
      id="primary-search-account-menu"
      keepMounted
      open={isMenuOpen}
      onClose={handleMenuClose}
    >
      <MenuItem onClick={handleMenuClose}>
        <Settings disableTooltip />
        Settings
      </MenuItem>
      <MenuItem onClick={handleMenuClose}>
        <Preferences disableTooltip />
        Preferences
      </MenuItem>
      <Divider />
      <MenuItem onClick={() => {
        context.setUser(guestUser);
        localStorage.setItem('user', JSON.stringify(guestUser));
        handleMenuClose();
        window.location.href = '/';
      }}>
        <SignOut disableTooltip />
        Sign Out
      </MenuItem>
    </Menu>
  );
};

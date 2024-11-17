import React, { Fragment, useContext } from 'react';
import { AppContext } from '../../../contexts';
import { Box, Menu, MenuItem } from '@mui/material';
import { Messages, Notifications, SignOut, Settings } from '../../Actions';
import { ThemeSwitcher } from '../ThemeSwitcher';
import { ThemeModeContext } from '../../../contexts';
import { guestUser } from 'contexts/AppContext';

interface MobileMenuProps {
  isMenuOpen: boolean;
  // eslint-disable-next-line no-unused-vars
  handleMenuOpen: (event: React.MouseEvent<HTMLElement>) => void;
  handleMenuClose: () => void;
  anchorEl: HTMLElement | null;
}

export const MobileMenu = ({
  isMenuOpen,
  // eslint-disable-next-line no-unused-vars
  handleMenuOpen,
  handleMenuClose,
  anchorEl
}: MobileMenuProps) => {
  const { toggleThemeMode } = useContext(ThemeModeContext);
  const context = useContext(AppContext);

  return (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right'
      }}
      id="primary-search-account-menu-mobile"
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right'
      }}
      open={isMenuOpen}
      onClose={handleMenuClose}
    >
      <Box sx={{ textAlign: 'center' }}>
        <MenuItem onClick={toggleThemeMode}>
          <ThemeSwitcher disableTooltip />
          Toggle Theme
        </MenuItem>
        {context.user.role !== 'guest' && (
          <Fragment>
            <MenuItem onClick={handleMenuClose}>
              <Messages total={0} disableTooltip />
              Messages
            </MenuItem>
            <MenuItem onClick={handleMenuClose}>
              <Notifications total={0} disableTooltip />
              Notifications
            </MenuItem>
            <MenuItem onClick={handleMenuClose}>
              <Settings disableTooltip />
              Settings
            </MenuItem>
            <MenuItem onClick={() => {
              context.setUser(guestUser);
              localStorage.setItem('user', JSON.stringify(guestUser));
              handleMenuClose();
              window.location.href = '/';
            }}>
              <SignOut disableTooltip />
              Sign Out
            </MenuItem>
          </Fragment>
        )}
      </Box>
    </Menu>
  );
};

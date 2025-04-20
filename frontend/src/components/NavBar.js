import React, { useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  CloudUpload as UploadIcon,
  Chat as ChatIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const navItems = [
  { name: 'Home', path: '/', icon: <HomeIcon /> },
  { name: 'Upload', path: '/upload', icon: <UploadIcon /> },
  { name: 'Chat', path: '/chat', icon: <ChatIcon /> },
];

const NavBar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const isActive = (path) => location.pathname === path;

  const drawer = (
    <Box sx={{ width: 250, pt: 2 }}>
      <Typography variant="h6" sx={{ px: 2, mb: 2, fontWeight: 'bold' }}>
        Document QA
      </Typography>
      <List>
        {navItems.map((item) => (
          <ListItem
            button
            component={RouterLink}
            to={item.path}
            key={item.name}
            onClick={handleDrawerToggle}
            sx={{
              backgroundColor: isActive(item.path) ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
              color: isActive(item.path) ? 'primary.main' : 'inherit',
              borderRadius: 1,
              mx: 1,
              mb: 1,
            }}
          >
            <ListItemIcon sx={{ color: isActive(item.path) ? 'primary.main' : 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ flexGrow: 0 }}>
      <AppBar position="static" color="default" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              fontWeight: 700,
              color: 'primary.main',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <motion.div
              initial={{ rotate: -10 }}
              animate={{ rotate: 0 }}
              transition={{ duration: 0.5 }}
            >
              <InfoIcon sx={{ mr: 1 }} />
            </motion.div>
            Document QA
          </Typography>

          <Box sx={{ flexGrow: 1 }} />

          {!isMobile && (
            <Box sx={{ display: 'flex' }}>
              {navItems.map((item) => (
                <Button
                  key={item.name}
                  component={RouterLink}
                  to={item.path}
                  sx={{
                    mx: 1,
                    color: isActive(item.path) ? 'primary.main' : 'text.primary',
                    fontWeight: isActive(item.path) ? 600 : 500,
                    position: 'relative',
                    '&:hover': {
                      bgcolor: 'transparent',
                    },
                  }}
                  disableRipple
                >
                  {item.icon && <Box component="span" sx={{ mr: 0.5, display: 'flex', alignItems: 'center' }}>{item.icon}</Box>}
                  {item.name}
                  {isActive(item.path) && (
                    <motion.div
                      layoutId="navbar-indicator"
                      style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: 3,
                        backgroundColor: theme.palette.primary.main,
                        borderRadius: 3,
                      }}
                      transition={{ type: 'spring', duration: 0.5 }}
                    />
                  )}
                </Button>
              ))}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: 260 },
        }}
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default NavBar; 
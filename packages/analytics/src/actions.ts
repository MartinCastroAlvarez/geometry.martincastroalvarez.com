/**
 * Google Analytics actions and categories for Geometry app.
 *
 * Type-safe constants for tracking so events stay consistent and avoid typos.
 */

export enum GoogleAnalyticsActions {
  PAGE_VIEW = "page_view",
  GEOMETRY_PAGE_VIEW = "geometry_page_view",

  NAV_JOBS = "geometry_nav_jobs",
  NAV_EDITOR = "geometry_nav_editor",
  NAV_HOME = "geometry_nav_home",
  NAV_GALLERY = "geometry_nav_gallery",

  USER_LOGIN = "geometry_login",
  USER_LOGOUT = "geometry_logout",

  GALLERY_VIEW = "geometry_gallery_view",
  JOB_VIEW = "geometry_job_view",
  EDITOR_OPEN = "geometry_editor_open",
}

export enum GoogleAnalyticsCategories {
  NAVIGATION = "Navigation",
  USER = "User",
  PAGE = "Page",
}

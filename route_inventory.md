# Complete Backend API Routes Inventory

## Authentication Routes (10 routes)
1. `POST /api/v1/auth/register` - User registration
2. `POST /api/v1/auth/login` - User login ✅ USED
3. `GET /api/v1/auth/me` - Get current user info
4. `PUT /api/v1/auth/me` - Update user profile
5. `POST /api/v1/auth/change-password` - Change password
6. `POST /api/v1/auth/api-keys` - Generate API keys
7. `GET /api/v1/auth/users` - List all users (admin)
8. `GET /api/v1/auth/stats` - User statistics
9. `POST /api/v1/auth/logout` - User logout ✅ USED
10. `GET /api/v1/auth/info` - Auth system info

## CVE Routes (12 routes)
11. `POST /api/v1/cve/search/advanced` - Advanced search ✅ USED
12. `POST /api/v1/cve/bulk-import` - Bulk import CVEs
13. `GET /api/v1/cve/search/history` - Search history
14. `POST /api/v1/cve/search/save` - Save search query
15. `GET /api/v1/cve/search/saved` - Get saved searches
16. `POST /api/v1/cve/search/saved/{search_id}/execute` - Execute saved search
17. `DELETE /api/v1/cve/search/saved/{search_id}` - Delete saved search
18. `POST /api/v1/cve/search` - Basic search
19. `POST /api/v1/cve/import-from-nvd` - Import from NVD
20. `GET /api/v1/cve/` - List CVEs ✅ USED
21. `GET /api/v1/cve/{cve_id}` - Get specific CVE ✅ PARTIALLY USED
22. `GET /api/v1/cve/stats/summary` - CVE statistics ✅ USED

## Analysis Routes (11 routes)
23. `POST /api/v1/analysis/analyze` - Analyze CVE ✅ USED
24. `GET /api/v1/analysis/{cve_id}/analysis` - Get analysis results
25. `POST /api/v1/analysis/risk-assessment` - Risk assessment
26. `POST /api/v1/analysis/{cve_id}/mitigations` - Get mitigations
27. `GET /api/v1/analysis/{cve_id}/attack-vectors` - Get attack vectors
28. `POST /api/v1/analysis/cve/analyze` - CVE analysis
29. `POST /api/v1/analysis/code/analyze` - Code analysis
30. `GET /api/v1/analysis/results/{analysis_id}` - Get analysis result
31. `GET /api/v1/analysis/results` - List analysis results
32. `GET /api/v1/analysis/ai/status` - AI service status
33. `POST /api/v1/analysis/ai/initialize` - Initialize AI service

## Dashboard Routes (4 routes)
34. `GET /api/v1/dashboard/metrics` - Dashboard metrics ✅ USED
35. `GET /api/v1/dashboard/recent-cves` - Recent CVEs
36. `GET /api/v1/dashboard/timeline` - Timeline data ✅ USED
37. `GET /api/v1/dashboard/stats` - Dashboard statistics

## Chat Routes (5 routes)
38. `POST /api/v1/chat/` - Send chat message ✅ USED
39. `GET /api/v1/chat/sessions` - Get chat sessions
40. `GET /api/v1/chat/history` - Get chat history
41. `GET /api/v1/chat/stats` - Chat statistics
42. `DELETE /api/v1/chat/sessions/{session_id}` - Delete chat session

## PoC Routes (4 routes)
43. `POST /api/v1/poc/generate` - Generate PoC ✅ USED
44. `GET /api/v1/poc/{cve_id}` - Get PoC for CVE
45. `GET /api/v1/poc/` - List PoCs
46. `POST /api/v1/poc/{cve_id}/validate` - Validate PoC

## Watchlist Routes (8 routes)
47. `POST /api/v1/watchlist/` - Create watchlist ✅ USED
48. `GET /api/v1/watchlist/` - List watchlists
49. `GET /api/v1/watchlist/{watchlist_id}` - Get watchlist
50. `DELETE /api/v1/watchlist/{watchlist_id}` - Delete watchlist
51. `POST /api/v1/watchlist/{watchlist_id}/cves` - Add CVEs to watchlist ✅ USED
52. `GET /api/v1/watchlist/{watchlist_id}/cves` - Get watchlist CVEs
53. `GET /api/v1/watchlist/{watchlist_id}/alerts` - Get watchlist alerts
54. `GET /api/v1/watchlist/stats/overview` - Watchlist statistics

## Reports Routes (7 routes)
55. `POST /api/v1/reports/generate` - Generate report
56. `GET /api/v1/reports/` - List reports
57. `GET /api/v1/reports/{report_id}` - Get report
58. `GET /api/v1/reports/{report_id}/download` - Download report
59. `DELETE /api/v1/reports/{report_id}` - Delete report
60. `GET /api/v1/reports/metrics/overview` - Report metrics
61. `GET /api/v1/reports/types/supported` - Supported report types

## Notifications Routes (12 routes)
62. `GET /api/v1/notifications/` - Get notifications
63. `POST /api/v1/notifications/` - Create notification
64. `PUT /api/v1/notifications/{notification_id}/read` - Mark as read
65. `PUT /api/v1/notifications/mark-all-read` - Mark all as read
66. `DELETE /api/v1/notifications/{notification_id}` - Delete notification
67. `DELETE /api/v1/notifications/clear-all` - Clear all notifications
68. `GET /api/v1/notifications/stats` - Notification statistics
69. `GET /api/v1/notifications/preferences` - Get preferences
70. `PUT /api/v1/notifications/preferences` - Update preferences
71. `POST /api/v1/notifications/test` - Test notification
72. `GET /api/v1/notifications/email-queue` - Email queue status
73. `POST /api/v1/notifications/cleanup` - Cleanup notifications

## Settings Routes (13 routes)
74. `GET /api/v1/settings/user` - Get user settings
75. `PUT /api/v1/settings/user` - Update user settings
76. `GET /api/v1/settings/notifications` - Get notification settings
77. `PUT /api/v1/settings/notifications` - Update notification settings
78. `GET /api/v1/settings/export` - Get export settings
79. `PUT /api/v1/settings/export` - Update export settings
80. `GET /api/v1/settings/system` - Get system settings
81. `PUT /api/v1/settings/system` - Update system settings
82. `GET /api/v1/settings/defaults` - Get default settings
83. `POST /api/v1/settings/reset` - Reset settings
84. `GET /api/v1/settings/export-all` - Export all settings
85. `POST /api/v1/settings/import-all` - Import all settings
86. `GET /api/v1/settings/validate` - Validate settings

## Monitoring Routes (6 routes)
87. `GET /api/v1/monitoring/health` - Health check
88. `GET /api/v1/monitoring/metrics` - System metrics
89. `GET /api/v1/monitoring/status` - System status
90. `GET /api/v1/monitoring/logs` - System logs
91. `POST /api/v1/monitoring/restart` - Restart system
92. `GET /api/v1/monitoring/performance` - Performance metrics

## Summary
- **Total Routes**: 92+ routes
- **Currently Used**: ~15 routes (16%)
- **Missing**: ~77 routes (84%)

## Priority for Frontend Integration
1. **High Priority** (Core Features): Auth, CVE details, Analysis results, Chat history
2. **Medium Priority** (User Experience): Notifications, Settings, Reports
3. **Low Priority** (Admin/Advanced): Monitoring, System management 
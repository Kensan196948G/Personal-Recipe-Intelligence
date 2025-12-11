/**
 * API Key Manager Component
 *
 * APIキーの発行・管理・使用量確認を行うコンポーネント
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  FormControlLabel,
  Checkbox,
  Grid,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon,
  Block as BlockIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const API_BASE_URL = '/api/v1/public';

const ApiKeyManager = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // ダイアログ状態
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [newKeyDialogOpen, setNewKeyDialogOpen] = useState(false);

  // 作成フォーム
  const [keyName, setKeyName] = useState('');
  const [permissions, setPermissions] = useState({
    read_recipes: true,
    write_recipes: false,
    delete_recipes: false,
    read_tags: true,
    write_tags: false
  });
  const [rateLimits, setRateLimits] = useState({
    requests_per_minute: 60,
    requests_per_hour: 1000,
    requests_per_day: 10000
  });

  // 選択されたキー
  const [selectedKey, setSelectedKey] = useState(null);
  const [selectedKeyUsage, setSelectedKeyUsage] = useState(null);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState(null);

  // 初期読み込み
  useEffect(() => {
    loadApiKeys();
  }, []);

  // APIキー一覧を読み込み
  const loadApiKeys = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/keys`);
      const result = await response.json();

      if (result.status === 'ok') {
        setApiKeys(result.data.keys);
      } else {
        setError(result.error || 'Failed to load API keys');
      }
    } catch (err) {
      setError(`Error loading API keys: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // APIキーを作成
  const createApiKey = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: keyName,
          ...permissions,
          ...rateLimits
        })
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setNewlyCreatedKey(result.data);
        setNewKeyDialogOpen(true);
        setCreateDialogOpen(false);
        setSuccess('API key created successfully');
        await loadApiKeys();

        // フォームをリセット
        setKeyName('');
        setPermissions({
          read_recipes: true,
          write_recipes: false,
          delete_recipes: false,
          read_tags: true,
          write_tags: false
        });
      } else {
        setError(result.error || 'Failed to create API key');
      }
    } catch (err) {
      setError(`Error creating API key: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // APIキーを削除
  const deleteApiKey = async (keyId) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/keys/${keyId}`, {
        method: 'DELETE'
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setSuccess('API key deleted successfully');
        await loadApiKeys();
      } else {
        setError(result.error || 'Failed to delete API key');
      }
    } catch (err) {
      setError(`Error deleting API key: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // APIキーを無効化
  const revokeApiKey = async (keyId) => {
    if (!confirm('Are you sure you want to revoke this API key?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/keys/${keyId}/revoke`, {
        method: 'PATCH'
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setSuccess('API key revoked successfully');
        await loadApiKeys();
      } else {
        setError(result.error || 'Failed to revoke API key');
      }
    } catch (err) {
      setError(`Error revoking API key: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // APIキーをローテーション
  const rotateApiKey = async (keyId) => {
    if (!confirm('Rotate this API key? The old key will be revoked.')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/keys/${keyId}/rotate`, {
        method: 'POST'
      });

      const result = await response.json();

      if (result.status === 'ok') {
        setNewlyCreatedKey(result.data);
        setNewKeyDialogOpen(true);
        setSuccess('API key rotated successfully');
        await loadApiKeys();
      } else {
        setError(result.error || 'Failed to rotate API key');
      }
    } catch (err) {
      setError(`Error rotating API key: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 使用量を取得
  const loadUsage = async (keyId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/usage/${keyId}`);
      const result = await response.json();

      if (result.status === 'ok') {
        setSelectedKeyUsage(result.data);
      }
    } catch (err) {
      console.error('Error loading usage:', err);
    }
  };

  // 詳細を表示
  const showDetails = async (key) => {
    setSelectedKey(key);
    await loadUsage(key.key_id);
    setDetailsDialogOpen(true);
  };

  // クリップボードにコピー
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard');
  };

  // 使用率を計算
  const calculateUsagePercentage = (current, limit) => {
    return Math.min((current / limit) * 100, 100);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* ヘッダー */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">API Key Management</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadApiKeys}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            disabled={loading}
          >
            Create API Key
          </Button>
        </Box>
      </Box>

      {/* アラート */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* APIキー一覧 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Key ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Permissions</TableCell>
              <TableCell>Usage</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading && apiKeys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <LinearProgress />
                </TableCell>
              </TableRow>
            ) : apiKeys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No API keys found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              apiKeys.map((key) => (
                <TableRow key={key.key_id}>
                  <TableCell>{key.name}</TableCell>
                  <TableCell>
                    <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                      {key.key_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={key.is_active ? 'Active' : 'Inactive'}
                      color={key.is_active ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {key.scope.read_recipes && <Chip label="Read" size="small" variant="outlined" />}
                      {key.scope.write_recipes && <Chip label="Write" size="small" variant="outlined" />}
                      {key.scope.delete_recipes && <Chip label="Delete" size="small" variant="outlined" color="error" />}
                    </Box>
                  </TableCell>
                  <TableCell>{key.usage_count} requests</TableCell>
                  <TableCell>
                    {new Date(key.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small" onClick={() => showDetails(key)}>
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Rotate Key">
                      <IconButton size="small" onClick={() => rotateApiKey(key.key_id)}>
                        <RefreshIcon />
                      </IconButton>
                    </Tooltip>
                    {key.is_active && (
                      <Tooltip title="Revoke Key">
                        <IconButton size="small" onClick={() => revokeApiKey(key.key_id)}>
                          <BlockIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete Key">
                      <IconButton size="small" color="error" onClick={() => deleteApiKey(key.key_id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* APIキー作成ダイアログ */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New API Key</DialogTitle>
        <DialogContent>
          <TextField
            label="Key Name"
            value={keyName}
            onChange={(e) => setKeyName(e.target.value)}
            fullWidth
            margin="normal"
            required
          />

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Permissions
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={permissions.read_recipes}
                onChange={(e) => setPermissions({ ...permissions, read_recipes: e.target.checked })}
              />
            }
            label="Read Recipes"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={permissions.write_recipes}
                onChange={(e) => setPermissions({ ...permissions, write_recipes: e.target.checked })}
              />
            }
            label="Write Recipes"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={permissions.delete_recipes}
                onChange={(e) => setPermissions({ ...permissions, delete_recipes: e.target.checked })}
              />
            }
            label="Delete Recipes"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={permissions.read_tags}
                onChange={(e) => setPermissions({ ...permissions, read_tags: e.target.checked })}
              />
            }
            label="Read Tags"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={permissions.write_tags}
                onChange={(e) => setPermissions({ ...permissions, write_tags: e.target.checked })}
              />
            }
            label="Write Tags"
          />

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Rate Limits
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <TextField
                label="Per Minute"
                type="number"
                value={rateLimits.requests_per_minute}
                onChange={(e) => setRateLimits({ ...rateLimits, requests_per_minute: parseInt(e.target.value) })}
                fullWidth
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                label="Per Hour"
                type="number"
                value={rateLimits.requests_per_hour}
                onChange={(e) => setRateLimits({ ...rateLimits, requests_per_hour: parseInt(e.target.value) })}
                fullWidth
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                label="Per Day"
                type="number"
                value={rateLimits.requests_per_day}
                onChange={(e) => setRateLimits({ ...rateLimits, requests_per_day: parseInt(e.target.value) })}
                fullWidth
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={createApiKey} variant="contained" disabled={!keyName || loading}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* 新規作成キー表示ダイアログ */}
      <Dialog open={newKeyDialogOpen} onClose={() => setNewKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>API Key Created</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This is the only time you'll see this key. Please save it securely!
          </Alert>

          {newlyCreatedKey && (
            <Box>
              <TextField
                label="API Key"
                value={newlyCreatedKey.api_key}
                fullWidth
                margin="normal"
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <IconButton onClick={() => copyToClipboard(newlyCreatedKey.api_key)}>
                      <CopyIcon />
                    </IconButton>
                  )
                }}
              />
              <TextField
                label="Key ID"
                value={newlyCreatedKey.key_info.key_id}
                fullWidth
                margin="normal"
                InputProps={{ readOnly: true }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewKeyDialogOpen(false)} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* 詳細ダイアログ */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>API Key Details</DialogTitle>
        <DialogContent>
          {selectedKey && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>Basic Information</Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <TextField label="Name" value={selectedKey.name} fullWidth InputProps={{ readOnly: true }} />
                </Grid>
                <Grid item xs={6}>
                  <TextField label="Key ID" value={selectedKey.key_id} fullWidth InputProps={{ readOnly: true }} />
                </Grid>
                <Grid item xs={6}>
                  <TextField label="Created" value={new Date(selectedKey.created_at).toLocaleString()} fullWidth InputProps={{ readOnly: true }} />
                </Grid>
                <Grid item xs={6}>
                  <TextField label="Last Used" value={selectedKey.last_used_at ? new Date(selectedKey.last_used_at).toLocaleString() : 'Never'} fullWidth InputProps={{ readOnly: true }} />
                </Grid>
              </Grid>

              {selectedKeyUsage && (
                <>
                  <Typography variant="subtitle2" gutterBottom>Usage Statistics</Typography>
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption">Last Minute</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={calculateUsagePercentage(
                          selectedKeyUsage.current_usage.last_minute,
                          selectedKeyUsage.rate_limits.per_minute
                        )}
                        sx={{ mb: 0.5 }}
                      />
                      <Typography variant="caption">
                        {selectedKeyUsage.current_usage.last_minute} / {selectedKeyUsage.rate_limits.per_minute}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption">Last Hour</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={calculateUsagePercentage(
                          selectedKeyUsage.current_usage.last_hour,
                          selectedKeyUsage.rate_limits.per_hour
                        )}
                        sx={{ mb: 0.5 }}
                      />
                      <Typography variant="caption">
                        {selectedKeyUsage.current_usage.last_hour} / {selectedKeyUsage.rate_limits.per_hour}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption">Last Day</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={calculateUsagePercentage(
                          selectedKeyUsage.current_usage.last_day,
                          selectedKeyUsage.rate_limits.per_day
                        )}
                        sx={{ mb: 0.5 }}
                      />
                      <Typography variant="caption">
                        {selectedKeyUsage.current_usage.last_day} / {selectedKeyUsage.rate_limits.per_day}
                      </Typography>
                    </Box>

                    <Typography variant="caption">
                      Total Requests: {selectedKeyUsage.total_requests}
                    </Typography>
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ApiKeyManager;

/**
 * Camera Service Tests
 * カメラサービスのテスト
 */

import { describe, test, expect, beforeEach, afterEach, mock } from 'bun:test';
import cameraService from '../js/camera-service.js';

describe('CameraService', () => {
  let mockStream;
  let mockVideoTrack;

  beforeEach(() => {
    // MediaDevices APIのモック
    mockVideoTrack = {
      stop: mock(() => {}),
      getCapabilities: mock(() => ({
        facingMode: ['user', 'environment'],
        zoom: { min: 1, max: 10 },
        torch: true
      })),
      getSettings: mock(() => ({
        width: 1920,
        height: 1080,
        facingMode: 'environment'
      })),
      applyConstraints: mock(async () => {})
    };

    mockStream = {
      getTracks: () => [mockVideoTrack],
      getVideoTracks: () => [mockVideoTrack]
    };

    global.navigator = {
      mediaDevices: {
        getUserMedia: mock(async () => mockStream),
        enumerateDevices: mock(async () => [
          { kind: 'videoinput', deviceId: 'camera1', label: 'Front Camera' },
          { kind: 'videoinput', deviceId: 'camera2', label: 'Back Camera' },
          { kind: 'audioinput', deviceId: 'mic1', label: 'Microphone' }
        ])
      }
    };
  });

  afterEach(() => {
    cameraService.stopCamera();
  });

  test('isSupported() should return true when MediaDevices is available', () => {
    expect(cameraService.isSupported()).toBe(true);
  });

  test('isSupported() should return false when MediaDevices is not available', () => {
    global.navigator.mediaDevices = undefined;
    expect(cameraService.isSupported()).toBe(false);
  });

  test('startCamera() should start camera stream', async () => {
    const stream = await cameraService.startCamera();

    expect(stream).toBe(mockStream);
    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled();
  });

  test('startCamera() should throw error when not supported', async () => {
    global.navigator.mediaDevices = undefined;

    await expect(cameraService.startCamera()).rejects.toThrow(
      'カメラAPIがサポートされていません'
    );
  });

  test('stopCamera() should stop all tracks', async () => {
    await cameraService.startCamera();
    cameraService.stopCamera();

    expect(mockVideoTrack.stop).toHaveBeenCalled();
  });

  test('switchCamera() should toggle facingMode', async () => {
    await cameraService.startCamera();
    const initialMode = cameraService.currentFacingMode;

    await cameraService.switchCamera();

    expect(cameraService.currentFacingMode).not.toBe(initialMode);
  });

  test('setResolution() should update resolution settings', async () => {
    await cameraService.setResolution(1280, 720);

    expect(cameraService.settings.width.ideal).toBe(1280);
    expect(cameraService.settings.height.ideal).toBe(720);
  });

  test('setFlash() should control torch', async () => {
    await cameraService.startCamera();
    await cameraService.setFlash(true);

    expect(mockVideoTrack.applyConstraints).toHaveBeenCalledWith({
      advanced: [{ torch: true }]
    });
  });

  test('setFlash() should warn when torch is not supported', async () => {
    mockVideoTrack.getCapabilities = mock(() => ({}));
    await cameraService.startCamera();

    const consoleSpy = mock(() => {});
    console.warn = consoleSpy;

    await cameraService.setFlash(true);

    expect(consoleSpy).toHaveBeenCalled();
  });

  test('getAvailableDevices() should return video input devices', async () => {
    const devices = await cameraService.getAvailableDevices();

    expect(devices).toHaveLength(2);
    expect(devices[0].kind).toBe('videoinput');
    expect(devices[1].kind).toBe('videoinput');
  });

  test('getCurrentSettings() should return track settings', async () => {
    await cameraService.startCamera();
    const settings = cameraService.getCurrentSettings();

    expect(settings).toEqual({
      width: 1920,
      height: 1080,
      facingMode: 'environment'
    });
  });

  test('getCurrentSettings() should return null when camera is not started', () => {
    const settings = cameraService.getCurrentSettings();
    expect(settings).toBeNull();
  });

  test('capturePhoto() should capture photo from video element', async () => {
    const mockVideo = {
      videoWidth: 1920,
      videoHeight: 1080
    };

    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: mock(() => ({
        drawImage: mock(() => {})
      })),
      toBlob: mock((callback) => {
        callback(new Blob(['test'], { type: 'image/jpeg' }));
      })
    };

    global.document = {
      createElement: mock(() => mockCanvas)
    };

    const blob = await cameraService.capturePhoto(mockVideo);

    expect(blob).toBeInstanceOf(Blob);
    expect(mockCanvas.width).toBe(1920);
    expect(mockCanvas.height).toBe(1080);
  });

  test('capturePhoto() should reject when blob creation fails', async () => {
    const mockVideo = {
      videoWidth: 1920,
      videoHeight: 1080
    };

    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: mock(() => ({
        drawImage: mock(() => {})
      })),
      toBlob: mock((callback) => {
        callback(null);
      })
    };

    global.document = {
      createElement: mock(() => mockCanvas)
    };

    await expect(cameraService.capturePhoto(mockVideo)).rejects.toThrow(
      '画像の生成に失敗しました'
    );
  });
});

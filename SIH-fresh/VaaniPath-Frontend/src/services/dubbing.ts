import api from './api';

interface DubbingRequest {
    input_path: string;
    source: string;
    target: string;
    jobId: string;
    course_id: string;
    mode?: string;
    voice?: string;
}

interface DubbingResponse {
    status: string;
    dubbed_video_url?: string;
    message?: string;
}

// Trigger dubbing process via backend
export const triggerDubbing = async (videoUrl: string, sourceLanguage: string, targetLanguage: string, videoId: string, courseId: string): Promise<DubbingResponse> => {
    try {
        // Call backend endpoint which will handle ML localizer communication
        const response = await api.get(`/processing/dubbing/${videoId}/${targetLanguage}`);
        return response.data;
    } catch (error) {
        console.error('Dubbing error:', error);
        throw error;
    }
};

// Check if dubbed version exists
export const checkDubbedVersion = async (videoId: string, language: string): Promise<string | null> => {
    try {
        const response = await api.get(`/videos/${videoId}/dubbed/${language}`);
        return response.data.url;
    } catch (error) {
        return null;
    }
};

// Poll for dubbing completion via backend
export const pollDubbingStatus = async (videoId: string, language: string, maxAttempts: number = 120): Promise<string | null> => {
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await api.get(`/processing/dubbing/${videoId}/${language}`);

            if (response.data.status === 'completed' && response.data.dubbed_video_url) {
                return response.data.dubbed_video_url;
            }

            if (response.data.status === 'failed') {
                throw new Error('Dubbing failed');
            }

            // Status is 'processing', continue polling
        } catch (error: any) {
            // If 404, dubbing hasn't started yet, continue polling
            if (error.response?.status !== 404) {
                console.error('Polling error:', error);
            }
        }

        // Wait 3 seconds before next poll
        await new Promise(resolve => setTimeout(resolve, 3000));
    }

    return null;
};

// Save dubbed version to backend
export const saveDubbedVersion = async (videoId: string, language: string, fileUrl: string): Promise<void> => {
    try {
        await api.post('/videos/dubbed', {
            video_id: videoId,
            language: language,
            file_url: fileUrl
        });
    } catch (error) {
        console.error('Error saving dubbed version:', error);
        throw error;
    }
};



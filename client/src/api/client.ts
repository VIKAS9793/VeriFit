import axios from 'axios';

// Create Axios instance with base URL
// Vite proxy forwards /api to Flask backend
export const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadResume = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/resumes', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

export const analyzeResume = async (resumeData: any) => {
    const response = await apiClient.post('/analyze', { resume: resumeData });
    return response.data;
};

export const matchJob = async (resumeData: any, jobDescription: string) => {
    const response = await apiClient.post('/match', {
        resume: resumeData,
        job_description: jobDescription,
    });
    return response.data;
};

export const requestRewrite = async (resumeData: any, options: any = {}) => {
    const response = await apiClient.post('/rewrite', {
        resume: resumeData,
        options,
    });
    return response.data;
};

/**
 * XAI Layer: Get human-readable explanations for scores
 */
export const explainScore = async (scoreData: any) => {
    const response = await apiClient.post('/explain', { score: scoreData });
    return response.data;
};

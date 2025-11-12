import axios, { AxiosError } from 'axios';
import type { SearchRequest, SearchResponse } from '../types';

export const searchProfiles = async (baseUrl: string, request: SearchRequest): Promise<SearchResponse> => {
  try {
    const response = await axios.post<SearchResponse>(`${baseUrl}/search`, request, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      if (axiosError.response) {
        throw new Error(axiosError.response.data?.detail || 'Search failed');
      } else if (axiosError.request) {
        throw new Error('Unable to connect to the server. Please make sure the API is running.');
      }
    }
    throw new Error(error instanceof Error ? error.message : 'An error occurred');
  }
};


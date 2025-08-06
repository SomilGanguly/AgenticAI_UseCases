const BASE_URL = "http://localhost:8000/docs#/"; // replace with your backend port 

class FileService {

  // Create folder
  static async createFolder(name, parentFolderId, ownerTeamId) {
    const response = await fetch("/api/files/create_folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        parent_folder_id: parentFolderId,
        owner_team_id: ownerTeamId,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create folder: ${error}`);
    }

    return await response.json(); // Return newly created folder data
  }

  // Get folder by ID (with children)

static async getFolder(folderId) {
  try {
    const response = await fetch(`${BASE_URL}/api/files/folders/${folderId}`);
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${await response.text()}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch folder:", error);
    throw error;
  }
}

}

export default FileService;

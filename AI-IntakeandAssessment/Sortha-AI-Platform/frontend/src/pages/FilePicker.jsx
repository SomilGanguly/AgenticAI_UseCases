import React, { useState, useEffect } from "react";
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  Box,
  Button,
  Typography,
  Divider
} from "@mui/material";
import FolderIcon from "@mui/icons-material/Folder";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import CloseIcon from "@mui/icons-material/Close";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { v4 as uuidv4 } from "uuid";

import GlobalService from "../services/GlobalService";
import GetRootFolder from "../sortha-api-library/routes/v1/files/getRootFolder";
import GetSubFolder from "../sortha-api-library/routes/v1/files/getSubFolder";
import GetFilesInFolder from "../sortha-api-library/routes/v1/files/getFilesInFolder";

const FilePickerContent = ({ onSelectFile, onClose }) => {
  const [tree, setTree] = useState(null);
  const [path, setPath] = useState(["Home"]);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState("");
  

  useEffect(() => {
    const fetchRoot = async () => {
      const client = GlobalService.getGlobalData("requestClient");
      const request = client.createRequest(new GetRootFolder());
      const data = await request.invoke();
      const mapped = data.map(folder => ({
        id: uuidv4(),
        backendId: folder.id,
        name: folder.name,
        type: "folder",
        children: []
      }));
      setTree({
        id: uuidv4(),
        name: "Home",
        type: "folder",
        children: mapped
      });
    };
    fetchRoot();
  }, []);

  const openFolder = async (folderName) => {
    const newPath = [...path, folderName];
    setPath(newPath);

    let node = tree;
    for (let i = 1; i < newPath.length; i++) {
      node = node.children.find(c => c.name === newPath[i] && c.type === "folder");
    }

    if (node.children.length > 0) return;

    const client = GlobalService.getGlobalData("requestClient");
    const subReq = client.createRequest(new GetSubFolder(node.backendId));
    const fileReq = client.createRequest(new GetFilesInFolder(node.backendId));

    const [subs, files] = await Promise.all([subReq.invoke(), fileReq.invoke()]);

    const mappedSubs = subs.map(folder => ({
      id: uuidv4(),
      backendId: folder.id,
      name: folder.name,
      type: "folder",
      children: []
    }));

    const mappedFiles = files.map(file => ({
      id: uuidv4(),
      backendId: file.id,
      name: file.name,
      type: "file"
    }));

    node.children = [...mappedSubs, ...mappedFiles];
    setTree({ ...tree });
  };

  const goBack = () => {
    if (path.length > 1) {
      setPath(path.slice(0, path.length - 1));
    }
  };

  const handleFileClick = (file) => {
    if (selectedFileId === file.backendId) {
      setSelectedFileId(null);
    } else {
      setSelectedFileId(file.backendId);
      setSelectedFileName(file.name);
    }
  };

  const handleDone = () => {
    if (selectedFileId && selectedFileName) {
    onSelectFile(selectedFileId, selectedFileName);
    }
  };

  if (!tree) return <Typography>Loading...</Typography>;

  let currentNode = tree;
  for (let i = 1; i < path.length; i++) {
    currentNode = currentNode.children.find(c => c.name === path[i] && c.type === "folder");
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          {path.length > 1 && (
            <IconButton onClick={goBack} sx={{ mr: 1 }}>
              <ArrowBackIcon />
            </IconButton>
          )}
          <Typography variant="h6">Select a File</Typography>
        </Box>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      <List sx={{ flex: 1, overflowY: 'auto', borderTop: '1px solid #ddd' }}>
        {currentNode.children.map((item, index) => (
          <React.Fragment key={item.id}>
            <ListItem
              button
              onClick={() =>
                item.type === "folder"
                  ? openFolder(item.name)
                  : handleFileClick(item)
              }
            >
              <ListItemIcon>
                {item.type === "folder" ? (
                  <FolderIcon color="primary" />
                ) : (
                  <InsertDriveFileIcon />
                )}
              </ListItemIcon>
              <ListItemText primary={item.name} />
              {item.type === "file" && (
                <Checkbox
                  checked={selectedFileId === item.backendId}
                  onChange={() => handleFileClick(item)}
                />
              )}
            </ListItem>
            {index < currentNode.children.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>

     
        <Button
            variant="contained"
            disabled={!selectedFileId}
            onClick={handleDone}
            sx={{ mt: 20, mb: 2, width: '20%', marginLeft: '430px' }}

        >
            Done
        </Button>
      </Box>
  );
};

export default FilePickerContent;

import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  Menu,
  MenuItem,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  TextField,
  InputAdornment,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import FolderIcon from "@mui/icons-material/Folder";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import SearchIcon from "@mui/icons-material/Search";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf"; // PDF
import TableChartIcon from "@mui/icons-material/TableChart"; // Excel
import SlideshowIcon from "@mui/icons-material/Slideshow";   // PowerPoint
import DescriptionIcon from "@mui/icons-material/Description";
import ImageIcon from "@mui/icons-material/Image";
import TextSnippetIcon from "@mui/icons-material/TextSnippet";
import ArchiveIcon from "@mui/icons-material/Archive";
import { v4 as uuidv4 } from "uuid";

import GlobalService from "../services/GlobalService";

// Api Imports
import CreateFolder from "../sortha-api-library/routes/v1/files/createFolder";
import CreateFile from "../sortha-api-library/routes/v1/files/createFile";
import DeleteFile from "../sortha-api-library/routes/v1/files/deleteFile";
import DeleteFolder from "../sortha-api-library/routes/v1/files/deleteFolder";
import GetRootFolder from "../sortha-api-library/routes/v1/files/getRootFolder";
import GetSubFolder from "../sortha-api-library/routes/v1/files/getSubFolder";
import GetFilesInFolder from "../sortha-api-library/routes/v1/files/getFilesInFolder";
import DownloadFile from "../sortha-api-library/routes/v1/files/downloadFile";

const FileExplorer = () => {
  const [fileTree, setFileTree] = useState(null);
  const [currentPath, setCurrentPath] = useState(["Home"]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [newFolderDialogOpen, setNewFolderDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [itemMenuAnchorEl, setItemMenuAnchorEl] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const fileInputRef = useRef(null)


  useEffect(() => {
  const fetchRootFolders = async () => {
    const client = GlobalService.getGlobalData('requestClient')
    const request = client.createRequest(new GetRootFolder());

    try {
      const data = await request.invoke();
      console.log("Root folders:", data);

      const mappedChildren = data.map((folder) => ({
        id: uuidv4(),
        backendId: folder.id,
        name: folder.name,
        type: "folder",
        mimeType: "folder",
        size: "-",
        children: [],
      }));

      const rootNode = {
        id: uuidv4(),
        name: "Home",
        type: "folder",
        mimeType: "folder",
        size: "-",
        children: mappedChildren,
      };

      setFileTree(rootNode);
    } catch (err) {
      console.error("Failed to fetch root folders:", err);
    }
  };

  fetchRootFolders();
}, []);



  const getCurrentFolder = () => {
    let node = fileTree;
    for (let i = 1; i < currentPath.length; i++) {
      node = node.children.find((c) => c.name === currentPath[i] && c.type === "folder");
    }
    return node;
  };

  const getCurrentFolderBackendId = () => {
  let node = fileTree;
  for (let i = 1; i < currentPath.length; i++) {
    node = node.children.find((c) => c.name === currentPath[i] && c.type === "folder");
  }
  return node.backendId || null;
};


  const openFolder = async (folderName) => {
  const newPath = [...currentPath, folderName];
  setCurrentPath(newPath);
  setSearchTerm("");

  let node = fileTree;
  for (let i = 1; i < newPath.length; i++) {
    node = node.children.find(c => c.name === newPath[i] && c.type === "folder");
  }
  if (node.children.length > 0) return;

  const client = GlobalService.getGlobalData('requestClient')

  // Fetch subfolders
  const subReq = client.createRequest(new GetSubFolder(node.backendId));

  // Fetch files
  const fileReq = client.createRequest(new GetFilesInFolder(node.backendId));

  try {
    const [subs, files] = await Promise.all([subReq.invoke(), fileReq.invoke()]);
    console.log("Subfolders received:", subs);
    console.log("Files received:", files);

    const mappedSubs = subs.map(folder => ({
      id: uuidv4(),
      backendId: folder.id,
      name: folder.name,
      type: "folder",
      mimeType: "folder",
      size: "-",
      children: [],
    }));

    const mappedFiles = files.map((file) => {
    const extension = file.name.split(".").pop().toLowerCase();
    const mimeMap = {
      pdf: "application/pdf",
      zip: "application/zip",
      doc: "application/msword",
      docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      xls: "application/vnd.ms-excel",
      xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      ppt: "application/vnd.ms-powerpoint",
      pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      txt: "text/plain",
      csv: "text/csv",
      json: "application/json",
      jpg: "image/jpeg",
      jpeg: "image/jpeg",
      png: "image/png",
      gif: "image/gif",
    };

    const inferredMimeType = mimeMap[extension] || "";

    return {
        id: uuidv4(),
        backendId: file.id,
        name: file.name,
        type: "file",
        mimeType: inferredMimeType,
        size: file.size ? `${(file.size / 1024).toFixed(1)} KB` : "-",
      };
    });

      node.children = [...mappedSubs, ...mappedFiles];
      setFileTree({ ...fileTree });
    } catch (err) {
      console.error("Error loading folder contents:", err);
    }
};


  const navigateTo = (index) => {
    setCurrentPath(currentPath.slice(0, index + 1));
    setSearchTerm("");
  };

  const handleOpenMenu = (e) => setAnchorEl(e.currentTarget);
  const handleCloseMenu = () => setAnchorEl(null);

  const handleCreateFolder = () => {
    setNewFolderName("");
    setNewFolderDialogOpen(true);
    handleCloseMenu();
  };

  const confirmCreateFolder = () => {
  if (!newFolderName.trim()) {
    setNewFolderDialogOpen(false);
    return;
  }

  const trimmedName = newFolderName.trim();
  const currentFolder = getCurrentFolder();

  const alreadyExists = currentFolder.children.some(
    (child) => child.type === "folder" && child.name.toLowerCase() === trimmedName.toLowerCase()
  );

  if (alreadyExists) {
    console.warn("Folder with same name already exists.");
    alert("A folder with this name already exists.");
    return;
  }

  handleFolderRequest(trimmedName);
  setNewFolderDialogOpen(false);
};


  const handleFolderRequest = (name) => {
    const client = GlobalService.getGlobalData('requestClient')
    const parentId = getCurrentFolderBackendId();
    const request = client.createRequest(new CreateFolder(name, parentId, 0));

    request
      .invoke()
      .then((data) => {
        console.log("Folder created successfully:", data);

        const currentFolder = getCurrentFolder();

        currentFolder.children.push({
          id: uuidv4(),
          backendId: data.id, // backend ID for delete
          name,
          type: "folder",
          mimeType: "folder",
          modified: new Date().toLocaleDateString(),
          size: "-",
          children: [],
        });

        setFileTree({ ...fileTree });
      })
      .catch((error) => {
        console.error("Error creating folder:", error);
      });
  };

  const handleFileUpload = (e) => {
    const uploadedFiles = Array.from(e.target.files);
    const currentFolder = getCurrentFolder();
    const client = GlobalService.getGlobalData('requestClient')

    uploadedFiles.forEach((file) => {
      const parentId = getCurrentFolderBackendId();
      const request = client.createRequest(new CreateFile(file, file.name, parentId));
      request
        .invoke()
        .then((data) => {
          console.log("Uploaded:", data);

          currentFolder.children.push({
            id: uuidv4(), // frontend ID for internal tree use
            backendId: data.id, // Backend ID used for deletion
            name: file.name,
            type: "file",
            mimeType: file.type,
            modified: new Date().toLocaleDateString(),
            size: `${(file.size / 1024).toFixed(1)} KB`,
            content: URL.createObjectURL(file),
          });
          setFileTree({ ...fileTree });
        })
        .catch((err) => {
          console.error("File upload failed:", err);
        });
    });

    e.target.value = "";
    handleCloseMenu();
  };

  const handleDownloadItem = async () => {
    if (!selectedItem || selectedItem.type !== "file") return;

    console.log("Download file:", selectedItem.name, "(ID:", selectedItem.backendId, ")");

    
    const client = GlobalService.getGlobalData('requestClient')
    const request = client.createRequest(new DownloadFile(selectedItem.backendId));
    request.invoke()
    .then((data) => {
      console.log("Download successful:");
      const blob = new Blob([data], { type: selectedItem.mimeType });
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = selectedItem.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    })
    .catch((err) => {
      console.error("Download failed:", err);
      alert("Failed to download file.");
    });

    handleItemMenuClose();
  };



  const handleItemMenuClick = (e, item) => {
    e.stopPropagation();
    setSelectedItem(item);
    setItemMenuAnchorEl(e.currentTarget);
  };

  const handleItemMenuClose = () => {
    setItemMenuAnchorEl(null);
    setSelectedItem(null);
  };

  const handleDeleteItem = () => {
    if (!selectedItem) {
      handleItemMenuClose();
      return;
    }

    const client = GlobalService.getGlobalData('requestClient')
    const backendId = selectedItem.backendId;

    if (!backendId) {
      console.warn("No backendId found for this item");
      handleItemMenuClose();
      return;
    }

    let request;

    if (selectedItem.type === "file") {
      request = client.createRequest(new DeleteFile(backendId));
    } else if (selectedItem.type === "folder") {
      request = client.createRequest(new DeleteFolder(backendId));
    } else {
      console.warn("Unknown item type:", selectedItem.type);
      handleItemMenuClose();
      return;
    }

    request
      .invoke()
      .then((data) => {
        console.log("Deleted:", data);

        const currentFolder = getCurrentFolder();
        currentFolder.children = currentFolder.children.filter(
          (child) => child !== selectedItem
        );
        setFileTree({ ...fileTree });
      })
      .catch((err) => {
        console.error("Delete failed:", err);
      });

    handleItemMenuClose();
  };


  const getReadableTypeLabel = (mimeType, type) => {
    if (type === "folder") return "Folder";
    if (!mimeType) return "-";
    const map = {
      "application/pdf": "PDF",
      "application/zip": "ZIP Archive",
      "application/msword": "Word Document",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Document",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel Spreadsheet",
      "application/vnd.ms-excel": "Excel Spreadsheet",
      "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint Presentation",
      "application/vnd.ms-powerpoint": "PowerPoint Presentation",
      "text/plain": "Text File",
      "application/json": "JSON File",
      "text/csv": "CSV File",
    };

    if (mimeType.startsWith("image/")) return "Image";
    if (mimeType.startsWith("text/")) return "Text File";
    return map[mimeType] || mimeType;
  };


  const renderIcon = (mime, type) => {
    if (type === "folder") return <FolderIcon sx={{ mr: 1 }} color="primary" />;
    if (mime === "application/pdf") return <PictureAsPdfIcon sx={{ mr: 1 }} color="error" />;
    if (
      mime === "application/msword" ||
      mime === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
      return <DescriptionIcon sx={{ mr: 1 }} color="primary" />;
    if (
      mime === "application/vnd.ms-excel" ||
      mime === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
      return <TableChartIcon sx={{ mr: 1 }} color="success" />;
    if (
      mime === "application/vnd.ms-powerpoint" ||
      mime === "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
      return <SlideshowIcon sx={{ mr: 1 }} color="warning" />;
    if (mime?.startsWith("image/")) return <ImageIcon sx={{ mr: 1 }} color="secondary" />;
    if (mime === "application/zip") return <ArchiveIcon sx={{ mr: 1 }} />;
    if (mime?.startsWith("text/") || mime === "application/json" || mime === "text/csv")
      return <TextSnippetIcon sx={{ mr: 1 }} color="action" />;
    return <InsertDriveFileIcon sx={{ mr: 1 }} />;
  };


   if (!fileTree) {
    return <Typography sx={{ p: 4 }}>Loading...</Typography>;
  }
  const currentFolder = getCurrentFolder();

  const filteredItems = currentFolder.children.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Breadcrumbs>
          {currentPath.map((folder, index) => (
            <Link
              key={index}
              underline="hover"
              color={index === currentPath.length - 1 ? "text.primary" : "inherit"}
              onClick={() => navigateTo(index)}
              sx={{ cursor: "pointer" }}
            >
              {folder}
            </Link>
          ))}
        </Breadcrumbs>

        <div>
          <Button variant="contained" onClick={handleOpenMenu} endIcon={<UploadIcon />}>
            New
          </Button>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
            <MenuItem onClick={handleCreateFolder}>New Folder</MenuItem>
            {currentPath.length > 1 && (
              <MenuItem onClick={() => fileInputRef.current.click()}>File Upload</MenuItem>
            )}
          </Menu>

          <input hidden ref={fileInputRef} type="file" multiple onChange={handleFileUpload} />
          {/* <input
            hidden
            ref={folderInputRef}
            type="file"
            webkitdirectory="true"
            directory=""
            multiple
            onChange={handleFolderUpload}
          /> */}
        </div>
      </Box>

      <Box sx={{ mb: 1 }}>
        <TextField
          placeholder="Search files or folders"
          variant="outlined"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '999px',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              px: 2,
              '& fieldset': {
                border: 'none',
              },
            },
            input: {
              padding: '10px 0',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <MoreVertIcon /> { }
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Box>
        <Table
          sx={{
            borderCollapse: "separate",
            borderSpacing: 0,
            '& td, & th': {
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
              borderLeft: 'none',
              borderRight: 'none',
            },
            '& th:first-of-type, & td:first-of-type': {
              pl: 1.5,
            },
            '& th:last-of-type, & td:last-of-type': {
              pr: 1.5,
            },
          }}
        >
          <TableHead>
              <TableRow sx={{ height: 50 }}>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Type</strong></TableCell>
                <TableCell><strong>Size</strong></TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredItems.map((item, index) => (
                <TableRow
                  key={index}
                  hover
                  onClick={() => item.type === "folder" && openFolder(item.name)}
                  sx={{ height: 50 }}
                >
                  <TableCell sx={{ py: 0.5, px: 1 }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {renderIcon(item.mimeType, item.type)}
                      <Typography
                        variant="body2"
                        noWrap
                        sx={{
                          flexGrow: 1,
                          fontWeight: 500,
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                      >
                        {item.name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ py: 0.5 }}>{getReadableTypeLabel(item.mimeType, item.type)}</TableCell>
                  <TableCell sx={{ py: 0.5 }}>{item.size || "-"}</TableCell>
                  <TableCell sx={{ py: 0.5 }} onClick={(e) => handleItemMenuClick(e, item)}>
                    <IconButton size="small">
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>

        </Table>
      </Box>


      <Dialog
        open={newFolderDialogOpen}
        onClose={() => setNewFolderDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            backgroundColor: "#2a2a2a",
            color: "#fff",
            px: 2,
            py: 3,
          },
        }}
      >
        <DialogTitle sx={{ fontSize: "1.5rem", mb: 1 }}>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Folder Name"
            fullWidth
            variant="outlined"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            sx={{ input: { color: "#fff" }, label: { color: "#bbb" } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewFolderDialogOpen(false)} sx={{ color: "#aaa" }}>Cancel</Button>
          <Button onClick={confirmCreateFolder} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <Menu
        anchorEl={itemMenuAnchorEl}
        open={Boolean(itemMenuAnchorEl)}
        onClose={handleItemMenuClose}
      >
        <MenuItem onClick={handleDeleteItem}>Delete</MenuItem>
        {selectedItem?.type === "file" && (
          <MenuItem onClick={handleDownloadItem}>Download</MenuItem>
        )}
      </Menu>
    </Box>
  );
};

export default FileExplorer;

import { Paper, Grid, Button, Card, Typography } from '@mui/material';
import { useState } from 'react';
import MarkdownPreview from '@uiw/react-markdown-preview';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import FilePickerContent from './FilePicker';
import Snackbar from '@mui/material/Snackbar';
import { CircularProgress, Box } from '@mui/material';
import GlobalConfigService from '../services/GlobalConfigService';

const TemplatesPage = (props) => {
    const [output, setOutput] = useState()
    const [fileId, setFileId] = useState();
    const [filePickerOpen, setFilePickerOpen] = useState(false);
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [fileName, setFileName] = useState("");
    const handleOpenFileDialog = () => setFilePickerOpen(true);
    const handleCloseFileDialog = () => setFilePickerOpen(false);
    const [isLoading, setIsLoading] = useState(false);


    const handleWorkflowRun = () => {
        setIsLoading(true);
        fetch(`${GlobalConfigService.API_BASE_URL}/api/workflows/execute/1`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "workflow_id": 1,
                "input_data": {
                    "inputs": {
                        "transcript_file": {
                            "type": "text",
                            "file_id": fileId
                        }
                    }
                }
            })
        })
        .then(res => res.json())
        .then(data => {
            const intr = setInterval(() => {
                fetch(`${GlobalConfigService.API_BASE_URL}/api/workflows/get_status/${data.request_id}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.result !== null) {

                            clearInterval(intr);
                             setIsLoading(false);
                            const formatedData = data;
                            if (formatedData.result) {
                                setOutput(formatedData.result);
                            }
                            else {
                                setOutput(formatedData);
                            }
                        }
                    })
            }, 1000)
        })
    }

    return <>
        <Grid size={9} item>
                    <Card sx={{ p: 1 }}>
                        <p>{props.description}</p>
                    </Card>
        </Grid>
        <Grid container spacing={2} sx={{ p: 2  }}>              
            <Grid item xs={3} >
                <Card sx={{ p: 2, bgcolor: '#1e1e1e', borderRadius: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold', color: '#fff' }}>
                            Input
                    </Typography>

                    <Paper
                            elevation={2}
                            sx={{
                            p: 2,
                            mb: 2,
                            bgcolor: '#2e2e2e',
                            borderRadius: 2
                            }}
                        >
                            <input
                            disabled = {true}
                            type="text"
                            value={fileName || "Select File to Process"}
                            style={{
                                width: '100%',
                                padding: '10px',
                                borderRadius: '6px',
                                border: 'none',
                                fontWeight: 'bold',
                                fontSize: '16px',                           
                                marginBottom: '10px'
                            }}
                            />
                            <Button
                            variant="contained"
                            sx={{
                                bgcolor: '#90caf9',
                                color: '#000',
                                width: '100%',
                                textTransform: 'none',
                                borderRadius: '6px',
                                '&:hover': { bgcolor: '#64b5f6' }
                            }}
                            onClick={handleOpenFileDialog}
                            >
                            Upload File
                            </Button>
                    </Paper>

                        <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold', color: '#fff' }}>
                            Run Workflow
                        </Typography>

                        <Paper
                            elevation={2}
                            sx={{
                            p: 2,
                            bgcolor: '#2e2e2e',
                            borderRadius: 2
                            }}
                        >
                            <Button
                            variant="contained"
                            sx={{
                                bgcolor: '#66bb6a',
                                width: '100%',
                                textTransform: 'none',
                                borderRadius: '6px',
                                '&:hover': { bgcolor: '#43a047' }
                            }}
                            onClick={handleWorkflowRun}
                            >
                            Run
                            </Button>
                        </Paper>
                        </Card>
                    </Grid>
                </Grid>
                <Grid size={12}>
                    <Paper sx={{ p: 2 }}>
                        <h3>Outputs: </h3>
                        {isLoading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <CircularProgress size={24} sx={{ mr: 2 }} />
                            <Typography variant="body1">Running workflow... Please wait.</Typography>
                            </Box>
                        ) : (
                            <MarkdownPreview
                            style={{ whiteSpace: 'pre-wrap' }}
                            source={output ? output : "No output yet"}
                            />
                        )}
                    </Paper>
                </Grid>

                <Dialog open={filePickerOpen} onClose={handleCloseFileDialog} maxWidth="sm" fullWidth>
                    <DialogContent sx={{ minHeight: "400px", minWidth: "500px" }}>
                        <FilePickerContent
                            onSelectFile={(id, name) => {
                                console.log("Selected File ID:", id);
                                console.log("File Name:", name);
                                setFileId(id);
                                setFileName(name);
                                setOpenSnackbar(true);
                                handleCloseFileDialog();
                            }}
                            onClose={handleCloseFileDialog}
                        />
                    </DialogContent>
                </Dialog>
                <Snackbar
                    open={openSnackbar}
                    autoHideDuration={1000}
                    onClose={() => setOpenSnackbar(false)}
                    anchorOrigin={{ vertical: 'top', horizontal: 'right'  }} 
                    message={`Uploaded: ${fileName}`}
                    />
    </>
}

export default TemplatesPage
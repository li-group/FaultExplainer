// import { useState, useEffect, useRef } from 'react';
// import { ScrollArea, Textarea, Button, Box } from '@mantine/core';
// import { useChat } from '../ChatContext';
// import { socket } from '../socket';


// export function ChatPage() {
//     const { messages, setMessages } = useChat();
//     // const [messages, setMessages] = useState<{ text: string, isUser: boolean }[]>([]); // Store chat messages
//     const [newMessage, setNewMessage] = useState(''); // Store new message input
//     const scrollAreaRef = useRef<HTMLDivElement>(null); // Ref to scroll to the end of the chat
//     const [isWaitingForReply, setIsWaitingForReply] = useState(false);

//     useEffect(() => {
//         scrollAreaRef.current!.scrollTo({ top: scrollAreaRef.current!.scrollHeight, behavior: 'smooth' });
//     }, [messages]);

//     useEffect(() => {
//         const receiveMessage = (data) => {
//             if (typeof data === 'string') {
//                 // Regular text message
//                 const msg = { text: data, isUser: false };
//                 setMessages(messages => [...messages, msg]);
//             } else if (data.images && data.message) {
//                 // Fault analysis message with graphs and text
//                 const combinedMessage = {
//                     text: (
//                         <div>
//                             <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'right' }}>
//                                 {data.images.map((graph, index) => (
//                                     <img key={index} src={`data:image/png;base64,${graph.image}`} alt={`Graph for ${graph.feature}`} style={{ maxWidth: '32%', height: 'auto' }} />
//                                 ))}
//                             </div>
//                             <p>{data.message}</p>
//                         </div>
//                     ),
//                     isUser: false
//                 };
//                 setMessages(messages => [...messages, combinedMessage]);
//             }
//             setIsWaitingForReply(false); // Server reply received, allow sending messages again
//         };

//         socket.on('chat_reply', receiveMessage);

//         return () => {
//             socket.off('chat_reply', receiveMessage);
//         };
//     }, []);


//     // Function to send a message
//     const sendMessage = () => {
//         if (newMessage.trim() && !isWaitingForReply) {
//             setMessages(messages => [...messages, { text: newMessage, isUser: true }]);
//             socket.emit('chat_message', newMessage);
//             setNewMessage('');
//             setIsWaitingForReply(true); // Start waiting for server reply

//             // setTimeout(() => {
//             //     // Simulate server response
//             //     const serverMessage = "SERVER MESSAGE"; // Replace with dynamic server message if needed
//             //     setMessages(messages => [...messages, { text: serverMessage, isUser: false }]);
//             //     setIsWaitingForReply(false); // Server reply received, allow sending messages again
//             // }, 1000); // Adjust the delay as needed to simulate server response time
//         }
//     };

//     return (
//         <Box style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 95px)' }}>
//             <ScrollArea viewportRef={scrollAreaRef} type='auto' style={{ flexGrow: 1 }}>
//                 <Box style={{ padding: '10px' }}>
//                     {messages.map((message, index) => (
//                         <Box
//                             key={index}
//                             style={{
//                                 display: 'flex',
//                                 justifyContent: message.isUser ? 'flex-end' : 'flex-start',
//                                 margin: '10px',
//                             }}>
//                             <Box
//                                 style={{
//                                     maxWidth: '70%',
//                                     backgroundColor: message.isUser ? '#1a73e8' : '#f1f3f4',
//                                     color: message.isUser ? 'white' : 'black',
//                                     padding: '10px',
//                                     borderRadius: '20px',
//                                     wordBreak: 'break-word',
//                                 }}
//                             >
//                                 {message.text}
//                             </Box>
//                         </Box>
//                     ))}
//                 </Box>
//             </ScrollArea>

//             <Box style={{ display: 'flex', padding: '5px' }}>
//                 <Textarea
//                     autosize
//                     minRows={1}
//                     maxRows={4}
//                     placeholder="Type your message here"
//                     value={newMessage}
//                     onChange={(e) => setNewMessage(e.target.value)}
//                     onKeyDown={(e) => {
//                         if (e.key === 'Enter' && !e.shiftKey && !isWaitingForReply) {
//                             e.preventDefault();
//                             sendMessage();
//                         }
//                     }}
//                     style={{ flexGrow: 1, marginRight: '10px' }}
//                 />
//                 <Button
//                     onClick={sendMessage}
//                     loading={isWaitingForReply}
//                     disabled={isWaitingForReply || newMessage.trim() === ''}>
//                     Send
//                 </Button>
//             </Box>
//         </Box>
//     );
// }











import { useState, useEffect, useRef } from 'react';
import { ScrollArea, Textarea, Button, Box } from '@mantine/core';
import { useChat } from '../ChatContext';
import { socket } from '../socket';


export function ChatPage() {
    const { messages, addMessage, isWaitingForReply, setIsWaitingForReply } = useChat();
    // const [messages, setMessages] = useState<{ text: string, isUser: boolean }[]>([]); // Store chat messages
    const [newMessage, setNewMessage] = useState(''); // Store new message input
    const scrollAreaRef = useRef<HTMLDivElement>(null); // Ref to scroll to the end of the chat
    // const [isWaitingForReply, setIsWaitingForReply] = useState(false);

    // Function to send a message
    const sendMessage = () => {
        if (newMessage.trim() && !isWaitingForReply) {
            addMessage({ text: newMessage, isUser: true });
            socket.emit('chat_message', newMessage);
            setNewMessage('');
            setIsWaitingForReply(true); // Start waiting for server reply

        }
    };

    useEffect(() => {
        scrollAreaRef.current!.scrollTo({ top: scrollAreaRef.current!.scrollHeight, behavior: 'smooth' });
    }, [messages]);

    return (
        <Box style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 95px)' }}>
            <ScrollArea viewportRef={scrollAreaRef} type='auto' style={{ flexGrow: 1 }}>
                <Box style={{ padding: '10px' }}>
                    {messages.map((message, index) => (
                        <Box
                            key={index}
                            style={{
                                display: 'flex',
                                justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                                margin: '10px',
                            }}>
                            <Box
                                style={{
                                    maxWidth: '70%',
                                    backgroundColor: message.isUser ? '#1a73e8' : '#f1f3f4',
                                    color: message.isUser ? 'white' : 'black',
                                    padding: '10px',
                                    borderRadius: '20px',
                                    wordBreak: 'break-word',
                                }}
                            >
                                {message.text}
                            </Box>
                        </Box>
                    ))}
                </Box>
            </ScrollArea>

            <Box style={{ display: 'flex', padding: '5px' }}>
                <Textarea
                    autosize
                    minRows={1}
                    maxRows={4}
                    placeholder="Type your message here"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey && !isWaitingForReply) {
                            e.preventDefault();
                            sendMessage();
                        }
                    }}
                    style={{ flexGrow: 1, marginRight: '10px' }}
                />
                <Button
                    onClick={sendMessage}
                    // loading={isWaitingForReply}
                    disabled={isWaitingForReply || newMessage.trim() === ''}>
                    Send
                </Button>
            </Box>
        </Box>
    );
}
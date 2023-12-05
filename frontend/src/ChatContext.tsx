import { createContext, useState, useContext, useEffect } from 'react';
import { socket } from './socket';
import ReactMarkdown from 'react-markdown';
import tep_flowsheet from "./assets/tep_flowsheet.png";


export const ChatContext = createContext(null);

export const useChat = () => useContext(ChatContext);

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {

    const intro = "The Tennessee Eastman process is a widely studied chemical production process that serves as a benchmark for testing process control strategies and operations. It involves feeding a mixture of gaseous reactants into a chemical reactor where several reactions take place to produce different liquid products. Some of these reactions are designed to produce the desired end-products, while others result in by-products.\n" +
        "\n" +
        "The reactions within the reactor are temperature-dependent and are characterized by Arrhenius rate laws, which means that the reaction rates increase with temperature. Due to different activation energies, some reactions are more sensitive to temperature changes than others.\n" +
        "\n" +
        "After the reactions occur, the mixture is cooled and passed through a phase separation process to separate the vapor from the liquids. The vapor phase is partially recycled back to the reactor, along with fresh reactants, to enhance efficiency and reduce waste. A portion of the recycle stream is purged to prevent the accumulation of inert materials and by-products which could disrupt the process.\n" +
        "\n" +
        "The liquid components are further processed to remove any unreacted materials. The final products are then sent to subsequent processes, which are not included in the process description. The entire process is closely monitored and controlled to maintain optimal operating conditions, ensuring the safety, quality, and efficiency of the production.\n" +
        "\n" +
        "The Tennessee Eastman process exemplifies a complex chemical process with multiple feedback loops and control systems, reflecting real-world industrial chemical manufacturing scenarios.\n";

    const [messages, setMessages] = useState([{
        text: (<span>
            <img src={tep_flowsheet} alt="Tennessee Eastman process schematic" style={{ maxWidth: '100%', height: 'auto' }} />
            <br />
            {intro}
        </span>), isUser: false
    }]);
    // const [messages, setMessages] = useState([]);
    const [isWaitingForReply, setIsWaitingForReply] = useState(false);

    const addMessage = (message) => {
        setMessages(messages => [...messages, message]);
    };

    useEffect(() => {
        const receiveMessage = (data) => {
            if (typeof data === 'string') {
                // Regular text message
                const msg = { text: <ReactMarkdown>{data}</ReactMarkdown>, isUser: false };
                addMessage(msg);
            } else if (data.images && data.message) {
                // Fault analysis message with graphs and text
                const combinedMessage = {
                    text: (
                        <div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'right' }}>
                                {data.images.map((graph, index) => (
                                    <img key={index} src={`data:image/png;base64,${graph.image}`} alt={`Graph for ${graph.feature}`} style={{ maxWidth: '32%', height: 'auto' }} />
                                ))}
                            </div>
                            {/* <p> */}
                            <ReactMarkdown>{data.message}</ReactMarkdown>
                            {/* </p> */}
                        </div>
                    ),
                    isUser: false
                };
                addMessage(combinedMessage);
            }
            setIsWaitingForReply(false); // Server reply received, allow sending messages again
        };

        socket.on('chat_reply', receiveMessage);

        return () => {
            socket.off('chat_reply', receiveMessage);
        };
    }, []);

    return (
        <ChatContext.Provider value={{ messages, addMessage, isWaitingForReply, setIsWaitingForReply }}>
            {children}
        </ChatContext.Provider>
    );
};

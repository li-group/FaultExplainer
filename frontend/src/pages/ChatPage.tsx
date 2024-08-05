import { useEffect, useRef, useState } from "react";
import {
  ScrollArea,
  Textarea,
  ActionIcon,
  Box,
  SimpleGrid,
  Image,
} from "@mantine/core";
import { IconSend2 } from "@tabler/icons-react";
import { useConversationState, ChatMessage } from "../App";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { marked } from "marked";

export default function QuestionsPage() {
  const { conversation, setConversation } = useConversationState();
  const [inputText, setInputText] = useState<string>("");
  const scrollAreaRef = useRef<HTMLDivElement>(null); // Ref to scroll to the end of the chat

  async function sendMessageToBackend(
    messages: { role: string; content: string }[],
    id: string
  ) {
    await fetchEventSource("http://localhost:8000/send_message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ data: messages, id: id }),
      async onopen(res) {
        if (res.ok && res.status === 200) {
          console.log("Connection made ", res);
        } else if (
          res.status >= 400 &&
          res.status < 500 &&
          res.status !== 429
        ) {
          console.log("Client-side error ", res);
        }
      },
      onmessage(event) {
        const parsedData = JSON.parse(event.data);
        setConversation((prevMessages) => {
          const index = prevMessages.findIndex(
            (message) => message.id === parsedData.id
          );
          if (index !== -1) {
            // Message with the same id found, update it
            const updatedMessages = [...prevMessages];
            updatedMessages[index] = {
              ...updatedMessages[index],
              text: updatedMessages[index].text + parsedData.content,
            };
            return updatedMessages;
          } else {
            // New message, add it to the array
            const newMessage: ChatMessage = {
              id: parsedData.id,
              role: "assistant",
              text: parsedData.content,
              images: parsedData.images,
              explanation: false,
            };
            return [...prevMessages, newMessage];
          }
        });
      },
      onclose() {
        console.log("Connection closed by the server");
      },
      onerror(err) {
        console.log("There was an error from server", err);
      },
    });
  }

  const submitChat = () => {
    if (inputText !== "") {
      // inputText should be non empty
      const new_input_msg: ChatMessage = {
        id: `user_msg-${
          conversation.filter((chat) => chat.role === "user").length
        }`,
        role: "user",
        text: inputText,
        images: [],
        explanation: false,
      };
      setInputText("");
      const messages = [
        ...conversation.map((msg) => ({ role: msg.role, content: msg.text })),
        { role: "user", content: inputText },
      ];
      setConversation((prevConv) => [...prevConv, new_input_msg]);
      sendMessageToBackend(messages, new_input_msg.id);
    }
  };

  useEffect(() => {
    scrollAreaRef.current!.scrollTo({
      top: scrollAreaRef.current!.scrollHeight,
      behavior: "auto",
    });
  }, [conversation]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 95px)",
      }}
    >
      <ScrollArea
        type="auto"
        viewportRef={scrollAreaRef}
        style={{ flexGrow: 1 }}
      >
        {/* Assign growth factor of 1 to chat display */}
        {conversation.map((msg, idx) => (
          <Box
            key={idx}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              margin: "10px",
            }}
          >
            <Box
              style={{
                maxWidth: "70%",
                backgroundColor: msg.role === "user" ? "#1a73e8" : "#f1f3f4",
                color: msg.role === "user" ? "white" : "black",
                padding: "10px",
                borderRadius: "20px",
                wordBreak: "break-word",
              }}
            >
              {msg.images && (
                <SimpleGrid cols={Math.min(msg.images.length, 3)}>
                  {(() => {
                    // Perform the calculation once per message
                    return msg.images.map((img, idx) => (
                      <Image
                        key={idx}
                        src={`data:image/png;base64,${img.image}`}
                        alt={`Graph for ${img.name}`}
                        radius="md"
                      />
                    ));
                  })()}
                </SimpleGrid>
              )}
              {msg.text && (
                <div
                  dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }}
                />
              )}
            </Box>
          </Box>
        ))}
      </ScrollArea>
      {/* Chat input has a growth factor of 0 i.e., it won't grow */}
      <Textarea
        radius="md"
        placeholder="Ask something here ..."
        autosize
        maxRows={3}
        rightSection={
          <ActionIcon
            variant="subtle"
            aria-label="Settings"
            onClick={submitChat}
          >
            <IconSend2 style={{ width: "100%", height: "100%" }} stroke={1.5} />
          </ActionIcon>
        }
        value={inputText}
        onChange={(event) => setInputText(event.currentTarget.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submitChat();
          }
        }}
      />
    </div>
  );
}

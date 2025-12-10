import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Brain, ChevronDown, ChevronUp } from 'lucide-react';

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  reasoning?: string;
  codeSnapshot?: string;
  rawContent?: string;  // Agent返回的完整原始内容
}

interface ChatPanelProps {
  conversation: ConversationMessage[];
  onSendMessage: (instruction: string) => Promise<void>;
  isGenerating: boolean;
  error: string | null;
}

const EXAMPLE_PROMPTS = [
  '创建一个简约的黑色表盘，白色指针',
  '做一个数字时钟，赛博朋克风格',
  '设计一个复古风格的怀表',
  '创建一个现代简约表盘，显示日期和星期',
  '做一个霓虹灯效果的数字表盘',
];

function MessageBubble({ message }: { message: ConversationMessage }) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [showRawContent, setShowRawContent] = useState(false);
  const isUser = message.role === 'user';
  const hasReasoning = message.role === 'assistant' && message.reasoning;
  const hasCode = message.role === 'assistant' && message.codeSnapshot;
  // 兼容snake_case和camelCase两种格式
  const rawContent = message.rawContent || (message as any).raw_content;
  const hasRawContent = message.role === 'assistant' && rawContent;

  const codeStats = hasCode ? {
    lines: message.codeSnapshot!.split('\n').length,
    chars: message.codeSnapshot!.length,
  } : null;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-700 text-gray-100'
        }`}
      >
        <div className="p-3">
          <div className="text-sm whitespace-pre-wrap">{message.content}</div>
          {message.timestamp && (
            <div className="text-xs opacity-60 mt-1">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>

        {hasCode && codeStats && (
          <div className="border-t border-gray-600">
            <button
              onClick={() => setShowCode(!showCode)}
              className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-600/50 transition-colors text-sm"
            >
              <div className="flex items-center gap-2 text-green-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span>生成的代码</span>
                <span className="text-xs opacity-75">({codeStats.lines} 行)</span>
              </div>
              {showCode ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showCode && (
              <div className="px-3 pb-3 pt-1">
                <div className="bg-gray-900 rounded p-2 text-xs text-gray-300 font-mono whitespace-pre-wrap max-h-96 overflow-y-auto border border-gray-600">
                  {message.codeSnapshot}
                </div>
              </div>
            )}
          </div>
        )}

        {hasReasoning && (
          <div className="border-t border-gray-600">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-600/50 transition-colors text-sm"
            >
              <div className="flex items-center gap-2 text-blue-300">
                <Brain className="w-4 h-4" />
                <span>Agent 思考过程</span>
              </div>
              {showReasoning ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showReasoning && (
              <div className="px-3 pb-3 pt-1">
                <div className="bg-gray-800 rounded p-2 text-xs text-gray-300 font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {message.reasoning}
                </div>
              </div>
            )}
          </div>
        )}

        {hasRawContent && (
          <div className="border-t border-gray-600">
            <button
              onClick={() => setShowRawContent(!showRawContent)}
              className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-600/50 transition-colors text-sm"
            >
              <div className="flex items-center gap-2 text-purple-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Agent 完整回复内容</span>
                <span className="text-xs opacity-75">({rawContent!.length} 字符)</span>
              </div>
              {showRawContent ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showRawContent && (
              <div className="px-3 pb-3 pt-1">
                <div className="bg-gray-900 rounded p-3 text-xs text-gray-300 whitespace-pre-wrap max-h-96 overflow-y-auto border border-gray-700">
                  {rawContent}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPanel({ conversation, onSendMessage, isGenerating, error }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [generatingTime, setGeneratingTime] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  useEffect(() => {
    if (isGenerating) {
      setGeneratingTime(0);
      timerRef.current = setInterval(() => {
        setGeneratingTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      setGeneratingTime(0);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isGenerating]);

  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;

    const userMessage = input.trim();
    setInput('');

    try {
      await onSendMessage(userMessage);
    } catch (error: any) {
      console.error('Send message error:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-400" />
          💬 对话交互
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          描述你想要的表盘，AI 将为你生成完整的 HTML 代码
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversation.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg mb-2">开始对话</p>
            <p className="text-sm mb-4">点击下方示例或输入自己的指令</p>
            <div className="grid gap-2 max-w-md mx-auto">
              {EXAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(prompt)}
                  className="text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 transition-colors"
                >
                  💡 {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {conversation.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {isGenerating && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-100 rounded-lg p-3 max-w-[85%]">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                <span className="text-sm">
                  AI 正在生成表盘代码...
                  {generatingTime > 0 && <span className="ml-2 text-xs opacity-75">({generatingTime}s)</span>}
                </span>
              </div>
                {generatingTime > 30 && (
                <div className="text-xs text-yellow-400 mt-2">
                  ⏳ AI 生成可能需要 1-3 分钟，请耐心等待...
                  </div>
                )}
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 rounded-lg p-3 text-sm">
            ❌ {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入指令，例如：创建一个简约的黑色表盘..."
            className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={3}
            disabled={isGenerating}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isGenerating}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-6 py-2 transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            发送
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          💡 提示：描述你想要的表盘样式，AI 会为你生成可以直接运行的 HTML 代码
        </div>
      </div>
    </div>
  );
}

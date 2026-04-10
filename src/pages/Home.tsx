import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  const handleStartTest = () => {
    navigate("/test");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col items-center justify-center text-center max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            MBTI已经过时，<span className="text-purple-600">SBTI</span>来了。
          </h1>
          <p className="text-lg text-gray-600 mb-12">
            一个更符合时代特点的人格测试，帮助你更好地了解自己。
          </p>
          <button
            className="px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all transform hover:scale-105 shadow-lg"
            onClick={handleStartTest}
          >
            开始测试
          </button>
          <div className="mt-16 text-sm text-gray-500">
            <p>© 2026 SBTI 人格测试</p>
            <p className="mt-2">
              <a href="https://bilibili.com" className="text-purple-600 hover:underline">
                B站@蛆肉儿串儿
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
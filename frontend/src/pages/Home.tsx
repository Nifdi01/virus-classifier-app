import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <section className="text-gray-600 body-font">
      <div className="container mx-auto flex px-5 py-20 items-center justify-center flex-col">
        <img
          className="lg:w-1/6 md:w-3/6 w-5/6 object-cover object-center rounded"
          alt="Nucleotide sequence classifier banner"
          src="/hero.svg"
        />
        <div className="text-center lg:w-2/3 w-full">
          <h1 className="title-font sm:text-4xl text-3xl mb-4 font-medium text-gray-900">
            Nucleotide sequence classifier
          </h1>
          <p className="mb-8 px-5 leading-relaxed">
            Classify viral sequences with machine learning models quickly and
            efficiently.
          </p>
          <div className="flex justify-center">
            <button
              onClick={() => navigate("/processor")}
              className="inline-flex text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none hover:bg-indigo-600 rounded text-lg cursor-pointer"
            >
              Start processing
            </button>
            <button
              onClick={() => navigate("/history")}
              className="ml-4 inline-flex text-gray-700 bg-gray-100 border-0 py-2 px-6 focus:outline-none hover:bg-gray-200 rounded text-lg cursor-pointer"
            >
              View history
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

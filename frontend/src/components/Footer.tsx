export default function Footer() {
  return (
    <footer className="text-gray-600 body-font">
      <div className="container px-5 py-8 mx-auto flex items-center sm:flex-row flex-col">
        <a
          href="/"
          className="flex title-font font-medium items-center md:justify-start justify-center text-gray-900"
        >
          <img src="/icons.svg" className="w-12 h-12 rounded-full"></img>
          <span className="ml-3 text-xl">Virus Classifier</span>
        </a>
        <p className="text-sm text-gray-500 sm:ml-4 sm:pl-4 sm:border-l-2 sm:border-gray-200 sm:py-2 sm:mt-0 mt-4">
          Virus Classifier
          <a
            href="https://github.com/Nifdi01"
            className="text-gray-600 ml-1"
            rel="noopener noreferrer"
            target="_blank"
          >
            @Nifdi01
          </a>
        </p>
      </div>
    </footer>
  );
}

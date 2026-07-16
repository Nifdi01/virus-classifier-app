import { Link } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/processor", label: "Processor" },
  // { to: "/history", label: "History" },
];

export default function Navbar() {
  return (
    <header className="text-gray-600 body-font">
      <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
        <a className="flex title-font font-medium items-center text-gray-900 md:mb-0">
          <img
            className="w-12 h-12 text-white rounded-full"
            src="/icons.svg"
          ></img>
          <span className="ml-3 text-xl">Virus Classifier</span>
        </a>
        <nav className="md:ml-auto flex flex-wrap items-center text-base justify-center">
          {LINKS.map((link) => {
            return (
              <Link
                key={link.to}
                to={link.to}
                className={"mr-5 hover:text-gray-900"}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

import { Link } from "react-router-dom";
import { SITE_SECTIONS } from "@/data/manifesto";
import { Reveal, SectionHeading } from "@/components/Reveal";

export function SiteMap() {
  return (
    <Reveal as="section" className="section-tight">
      <div className="container">
        <SectionHeading
          eyebrow="Карта сайта"
          title="Все разделы витрины"
          lead="Короткая навигация, если хочется сразу прыгнуть в нужный кусок."
        />
        <div className="sitemap">
          {SITE_SECTIONS.map((section) => (
            <Link key={section.path} to={section.path} className="sitemap__item">
              <span className="sitemap__path">{section.path}</span>
              <strong>{section.name}</strong>
              <span className="sitemap__purpose">{section.purpose}</span>
            </Link>
          ))}
        </div>
      </div>
    </Reveal>
  );
}

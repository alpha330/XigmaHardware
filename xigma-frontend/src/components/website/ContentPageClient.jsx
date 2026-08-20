'use client';

import styled from '@emotion/styled';


const Page = styled.main`
  max-width: 960px;
  margin: 0 auto;
  padding: 4rem 2rem;
`;

const Header = styled.header`
  margin-bottom: 2rem;
  text-align: center;

  h1 {
    color: ${({ theme }) => theme.colors.textMain};
    font-size: clamp(2rem, 5vw, 3rem);
    margin-bottom: 1rem;
  }

  p {
    color: ${({ theme }) => theme.colors.textMuted};
    line-height: 1.8;
  }
`;

const Content = styled.article`
  background: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  color: ${({ theme }) => theme.colors.textMain};
  line-height: 2;
  padding: clamp(1.5rem, 4vw, 3rem);

  h2, h3 {
    color: ${({ theme }) => theme.colors.primary};
    margin: 2rem 0 1rem;
  }

  p, ul, ol {
    margin-bottom: 1.25rem;
  }
`;

export default function ContentPageClient({ title, summary, content }) {
  return (
    <Page>
      <Header>
        <h1>{title}</h1>
        {summary && <p>{summary}</p>}
      </Header>
      <Content dangerouslySetInnerHTML={{ __html: content }} />
    </Page>
  );
}
